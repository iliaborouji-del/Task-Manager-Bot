import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis

from config import BOT_TOKEN, REDIS_URL

async def main():
    redis = Redis(
        REDIS_URL,
        encoding="utf-8",
        decode_responses=True
    )
    storage = RedisStorage(redis=redis)
    
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=storage)
    
    await dp.start_polling(bot)
    
if __name__=='__main__':
    asyncio.run(main())