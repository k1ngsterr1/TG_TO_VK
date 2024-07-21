from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode

from handlers import router
token = sys.argv[1]
from relations import Relations

relations = Relations()
dp = Dispatcher(relations=relations, storage=MemoryStorage())
dp.include_router(router)
bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

