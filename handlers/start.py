from aiogram import Router, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message
import sys


channel = sys.argv[2]
inviteLink = sys.argv[3]

router = Router()


@router.message(CommandStart())
async def start(m: Message, bot: Bot):
    is_member = await bot.get_chat_member(channel, m.from_user.id)
    if is_member.status != "left":
        await m.answer("Привет:)\n"
                       "Что бы связаться телеграм канал с группой вк, используйте команду /add")
    else:
        await m.answer(f"Вам нужно подписаться на канал, для использования бота.\nКанал: {inviteLink}")
