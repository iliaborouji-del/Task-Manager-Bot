import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis

from config import Config

redis = Redis(
    Config.REDIS_HOST,
    Config.REDIS_PORT,
    Config.REDIS_DB,
    encoding="utf-8",
    decode_responses=True
)
storage = RedisStorage(redis=redis)
    
bot = Bot(token=Config.BOT_TOKEN)
dp = Dispatcher(storage=storage)
    
async def main():
    await dp.start_polling(bot)
    
if __name__=='__main__':
    asyncio.run(main())