import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.telegram import TelegramAPIServer
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis

from config import Config
from bot.handlers.start import router as start
from bot.handlers.add_task import router as add_task

redis = Redis(
    host=Config.REDIS_HOST,
    port=Config.REDIS_PORT,
    db=Config.REDIS_DB,
    encoding="utf-8",
    decode_responses=True
)
storage = RedisStorage(redis=redis)

SESSION = AiohttpSession(api=TelegramAPIServer.from_base("https://tapi.bale.ai"))
    
bot = Bot(token=Config.BOT_TOKEN, session=SESSION)
dp = Dispatcher(storage=storage)

dp.include_router(start)
dp.include_router(add_task)
    
async def main():
    await dp.start_polling(bot)
    
if __name__=='__main__':
    asyncio.run(main())