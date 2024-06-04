from aiogram import Router, Bot
from aiogram.filters import ChatMemberUpdatedFilter
from aiogram.types import ChatMemberUpdated
from aiogram.filters.chat_member_updated import \
    ChatMemberUpdatedFilter, KICKED, LEFT, \
    RESTRICTED, MEMBER, ADMINISTRATOR, CREATOR

router = Router()


@router.chat_member(ChatMemberUpdatedFilter(member_status_changed=LEFT >> MEMBER))
async def new_member(event: ChatMemberUpdated, bot: Bot):
    user_id = event.from_user.id
    await bot.send_message(user_id, "Вы успешно вступили в канал, теперь вы можете использовать команду /start")
