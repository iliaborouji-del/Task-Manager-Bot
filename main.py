import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.telegram import TelegramAPIServer
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis
import logging

from config import Config
from bot.handlers.start import router as start
from bot.handlers.add_task import router as add_task
from bot.handlers.show_tasks import router as show_tasks
from bot.handlers.report import router as report
from bot.handlers.show_all_tasks import router as all_tasks
from bot.database.connection import create_db

logger = logging.getLogger(__name__)

if Config.SOURCE == "telegram":
    SESSION = None
else:
    SESSION = AiohttpSession(api=TelegramAPIServer.from_base(Config.API_BASE_BALE))

bot = Bot(token=Config.BOT_TOKEN, session=SESSION)

redis = Redis(
    host=Config.REDIS_HOST,
    port=Config.REDIS_PORT,
    db=Config.REDIS_DB,
    encoding="utf-8",
    decode_responses=True
)
storage = RedisStorage(redis=redis)
dp = Dispatcher(storage=storage)

dp.include_router(start)
dp.include_router(add_task)
dp.include_router(show_tasks)
dp.include_router(report)
dp.include_router(all_tasks)
    
async def main():
    await create_db()
    logger.info("Database initialized successfully.")
    try:
        await dp.start_polling(bot)
        logger.info("Bot started in %s mode.", Config.SOURCE)
    finally:
        await bot.session.close()
        logger.info("Bot session closed.")
        await redis.close()
        logger.info("Redis connection closed.")
    
if __name__=='__main__':
    asyncio.run(main())