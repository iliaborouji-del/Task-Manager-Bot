import redis.asyncio as redis
from config import Config

qr_redis = redis.Redis(
    host=Config.REDIS_HOST,
    port=int(Config.REDIS_PORT),
    db=int(Config.REDIS_DB),
    decode_responses=False
)