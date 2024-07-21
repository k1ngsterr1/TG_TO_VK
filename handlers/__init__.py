from aiogram import Router

from . import start, add, forward, new_chat_member

router = Router()
router.include_router(start.router)
router.include_router(add.router)
router.include_router(forward.router)
router.include_router(new_chat_member.router)
