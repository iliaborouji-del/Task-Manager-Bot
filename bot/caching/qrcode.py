from typing import Optional
from bot.caching.client import qr_redis

QR_EXPIRE_SECONDS = 7 * 24 * 60 * 60

def qr_key(task_id: int) -> str:
    return f"qr:{task_id}"

async def cache_qr(task_id: int, image_bytes: bytes):
    return await qr_redis.setex(qr_key(task_id), QR_EXPIRE_SECONDS, image_bytes)
    
async def load_qr(task_id: int) -> Optional[bytes]:
    return await qr_redis.get(qr_key(task_id))

async def delete_qr(task_id: int) -> None:
    key = qr_key(task_id)
    return await qr_redis.delete(key)