import asyncio
import json
import httpx
import random
from aiogram import Router, Bot
from aiogram.types import Message
from relations import Relations
from urllib.parse import quote

router = Router()
context = {}

class VkMedia:
    def __init__(self, vk_token: str):
        self.vk_token = vk_token

    def get_vk_upload_server(self, media_type='photo'):
        params = {
            'access_token': self.vk_token,
            'v': '5.199'
        }
        if media_type == 'photo':
            response = httpx.get('https://api.vk.com/method/photos.getWallUploadServer', params=params)
        elif media_type == 'video':
            response = httpx.get('https://api.vk.com/method/video.save', params=params)
        else:
            raise ValueError("Unsupported media type")
    
        return response.json()['response']['upload_url']
    
    @classmethod
    def upload_media_to_vk(cls, upload_url, file_content, media_type='photo'):
        files = {
            'photo': ('photo.jpg', file_content, 'image/jpeg')
        } if media_type == 'photo' else {
            'video_file': ('video.mp4', file_content, 'video/mp4')
        }
        response = httpx.post(upload_url, files=files)
        return response.json()

    def save_media_to_vk(self, uploaded_media, media_type='photo'):
        params = {
            'access_token': self.vk_token,
            'v': '5.199'
        }
        if media_type == 'photo':
            params.update({
                'photo': uploaded_media['photo'],
                'server': uploaded_media['server'],
                'hash': uploaded_media['hash'],
            })
            response = httpx.post('https://api.vk.com/method/photos.saveWallPhoto', params=params)
        elif media_type == 'video':
            params.update({
                'video_id': uploaded_media['video_id'],
                'owner_id': uploaded_media['owner_id'],
                'title': 'Uploaded Video',
                'wall_post': 1,
                'is_private': 0,
                'privacy_view': 'all'
            })
            response = httpx.post('https://api.vk.com/method/video.save', params=params)
        else:
            raise ValueError("Unsupported media type")
        return response.json()

    def get_media(self, media_data, media_type='photo') -> tuple:
        upload_url = self.get_vk_upload_server(media_type=media_type)
        media = self.upload_media_to_vk(upload_url, media_data, media_type=media_type)
        saved_media = self.save_media_to_vk(media, media_type=media_type)
        if media_type == 'photo':
            return saved_media["response"][0]["owner_id"], saved_media["response"][0]["id"]
        elif media_type == 'video':
            return saved_media["response"]["owner_id"], saved_media["response"]["video_id"]


@router.channel_post()
async def forward(m: Message, bot: Bot, relations: Relations):
    group_id = f"{m.media_group_id}" if m.media_group_id else f"{m.chat.id}_{m.message_id}"
    file = None
    media_type = None
    if m.photo:
        file = await bot.get_file(m.photo[-1].file_id)
        media_type = 'photo'
    elif m.video:
        file = await bot.get_file(m.video.file_id)
        media_type = 'video'
    elif m.audio:
        file = await bot.get_file(m.audio.file_id)
        media_type = 'audio'

    if not context.get(f"text_{group_id}"):
        context[f"text_{group_id}"] = quote(m.text) if m.text else quote(m.caption)

    if file:
        file_content = (httpx.get(f'https://api.telegram.org/file/bot{bot.token}/{file.file_path}')).content
        if context.get(group_id):
            context[group_id].append((file_content, media_type))
        else:
            context[group_id] = [(file_content, media_type)]
            await asyncio.sleep(2)
    list_relations = relations.read()
    if str(m.chat.id) in list_relations:
        vk_groups = list_relations[str(m.chat.id)]

        for item in vk_groups:
            #if item[1] == 0:
            #    continue
            vk_name, vk_id, vk_token = item[0]
            users = httpx.get(f"https://api.vk.com/method/users.get?access_token={vk_token}&v=5.199")
            user_id = users.json()['response'][0]['id']
            where_to_post = item[1]
        
            if where_to_post < 1 or where_to_post >3:
                where_to_post = 1
            print(f"{where_to_post=}")
            attachments = []
            if file:
                for file_content, media_type in context[group_id]:
                    owner_id, media_id = VkMedia(vk_token).get_media(file_content, media_type)
                    attachments.append(f"{media_type}{owner_id}_{media_id}")

                if where_to_post == 1:
                    httpx.post(
                        f"https://api.vk.com/method/wall.post?owner_id=-{vk_id}&from_group=1&message={context[f'text_{group_id}']}&attachments={','.join(attachments)}&v=5.199",
                        headers={"Authorization": f"Bearer {vk_token}"})
                elif where_to_post == 2:
                    httpx.post(
                        f"https://api.vk.com/method/wall.post?owner_id={owner_id}&from_group=0&message={context[f'text_{group_id}']}&attachments={','.join(attachments)}&v=5.199",
                        headers={"Authorization": f"Bearer {vk_token}"})
                elif where_to_post == 3:
                    httpx.post(
                        f"https://api.vk.com/method/wall.post?owner_id=-{vk_id}&from_group=1&message={context[f'text_{group_id}']}&attachments={','.join(attachments)}&v=5.199",
                        headers={"Authorization": f"Bearer {vk_token}"})                    
                    httpx.post(
                        f"https://api.vk.com/method/wall.post?owner_id={owner_id}&from_group=0&message={context[f'text_{group_id}']}&attachments={','.join(attachments)}&v=5.199",
                        headers={"Authorization": f"Bearer {vk_token}"})
            else:
                if where_to_post == 1:
                    httpx.post(
                        f"https://api.vk.com/method/wall.post?owner_id=-{vk_id}&from_group=1&message={context[f'text_{group_id}']}&v=5.199",
                        headers={"Authorization": f"Bearer {vk_token}"})
                elif where_to_post == 2:
                    httpx.post(
                        f"https://api.vk.com/method/wall.post?owner_id={user_id}&from_group=1&message={context[f'text_{group_id}']}&v=5.199",
                        headers={"Authorization": f"Bearer {vk_token}"})
                elif where_to_post == 3:
                    httpx.post(
                        f"https://api.vk.com/method/wall.post?owner_id=-{vk_id}&from_group=1&message={context[f'text_{group_id}']}&v=5.199",
                        headers={"Authorization": f"Bearer {vk_token}"})        
                    httpx.post(
                        f"https://api.vk.com/method/wall.post?owner_id={user_id}&from_group=1&message={context[f'text_{group_id}']}&v=5.199",
                        headers={"Authorization": f"Bearer {vk_token}"})           
