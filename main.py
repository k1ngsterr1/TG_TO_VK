import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode

from relations import Relations
from handlers import router
token = sys.argv[1]



relations = Relations()
dp = Dispatcher(relations=relations, storage=MemoryStorage())
dp.include_router(router)
bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(dp.start_polling(bot))
