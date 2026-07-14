import os, time, hmac, hashlib, base64, urllib.parse
from typing import Optional
import aiohttp

QR_SECRET = os.getenv("QR_SECRET")
if not QR_SECRET:
    raise RuntimeError("QR_SECRET id not set. Please set QR_SECRET in your .env file.")
BOT_USERNAME = os.getenv("BOT_USERNAME", "tasks_manager_bot")
QR_API_URL = os.getenv("QR_API_URL", "https://api.qrserver.com/v1/create-qr-code/")
BALE_CHAT_BASE = os.getenv("BALE_CHAT_BASE", "https://web.bale.ai/chat?uid=1322664071")

def make_bale_link(payload: str) -> str:
    safe = urllib.parse.quote_plus(payload)
    sep = "&" if "?" in BALE_CHAT_BASE else "?"
    return f"{BALE_CHAT_BASE}{sep}start=task_{safe}"

def make_payload(task_id: int) -> int:
    ts = int(time.time())
    data = f"{task_id}|{ts}"
    sig = hmac.new(QR_SECRET.encode(), data.encode(), hashlib.sha256).digest()
    raw = data.encode() + b"|" + sig
    token = base64.urlsafe_b64encode(raw).decode()
    return token

def verify(token: str, max_age_secound: int = 60*60*24*30) -> int:
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
    expected = hmac.new(QR_SECRET.encode(), data, hashlib.sha256).digest()
    
    if not hmac.compare_digest(expected, sig):
        return None
    
    if time.time() - ts > max_age_secound:
        return None
    
    return task_id
    
async def generate_qr(link: str, size: str = 300*300, time_out: int = 15) -> Optional[bytes]:
    params = {"data": link, "size": size}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(QR_API_URL, params=params, timeout=time_out) as resp:
                if resp == 200:
                    return await resp.read()
    except Exception:
        return None
    return None