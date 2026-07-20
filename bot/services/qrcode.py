import time, hmac, hashlib, base64, urllib.parse
from typing import Optional
import aiohttp
from config import Config
from bot.caching.qrcode import cache_qr, load_qr

if not Config.QR_SECRET:
    raise RuntimeError("QR_SECRET is not set. Please set QR_SECRET in your .env file.")

def make_payload(task_id: int) -> int:
    ts = int(time.time())
    data = f"{task_id}|{ts}"
    sig = hmac.new(Config.QR_SECRET.encode(), data.encode(), hashlib.sha256).digest()
    raw = data.encode() + b"|" + sig
    token = base64.urlsafe_b64encode(raw).decode()
    return token

def verify(token: str, max_age_seconds: int = 60*60*24*30) -> int:
    try:
        token = urllib.parse.unquote_plus(token)
        token_fixed = token + "=" * (-len(token) % 4)
        raw = base64.urlsafe_b64decode(token_fixed.encode())
    except:
        return None
    
    parts = raw.split(b"|")
    if len(parts) < 3:
        return None
    
    try:
        task_id = int(parts[0].decode())
        ts = int(parts[1].decode())
    except:
        return None
    
    sig = b"|".join(parts[2:])
    data = f"{task_id}|{ts}".encode()
    expected = hmac.new(Config.QR_SECRET.encode(), data, hashlib.sha256).digest()
    
    if not hmac.compare_digest(expected, sig):
        return None
    
    if time.time() - ts > max_age_seconds:
        return None
    
    return task_id
    
async def generate_qr(link: str, size: str = "300*300", time_out: int = 15) -> Optional[bytes]:
    params = {"data": link, "size": size}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(Config.QR_API_URL, params=params, timeout=time_out) as resp:
                if resp.status == 200:
                    return await resp.read()
    except Exception:
        return None
    return None

def make_bale_link(payload: str) -> str:
    safe = urllib.parse.quote_plus(payload)
    sep = "&" if "?" in Config.CHAT_BASE else "?"
    return f"{Config.CHAT_BASE}{sep}start=task_{safe}"

def make_telegram_link(payload: str) -> str:
    safe = urllib.parse.quote_plus(payload)
    message_text = f"/start task_{safe}"
    encoded_message = urllib.parse.quote_plus(message_text)
    # Use text= parameter to pre-fill the message box
    return f"{Config.CHAT_BASE}?text={encoded_message}"

async def generate_qr_image(link: str, size: str = "300*300", timeout: int = 15) -> Optional[bytes]:
    params = {"data": link, "size": size}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(Config.QR_API_URL, params=params, timeout=timeout) as resp:
                if resp.status == 200:
                    return await resp.read()
    except Exception:
        return None
    return None

async def get_or_create_qr(task_id: int) -> bytes:
    payload = make_payload(task_id)
    if Config.SOURCE == "telegram":
        link = make_telegram_link(payload)
    else:
        link = make_bale_link(payload)
    
    # Cache the new link for future use
    await cache_qr(task_id, link)
    img_bytes = await generate_qr_image(link)
    return img_bytes