import os
from dotenv import load_dotenv

SOURCE = os.getenv("SOURCE", "telegram")

if SOURCE == "telegram":
    load_dotenv(".env.telegram")
else:
    load_dotenv(".env.bale")

class Config():
    SOURCE = SOURCE
    BOT_TOKEN = os.getenv("TOKEN")
    API_BASE = os.getenv("API_BASE")
    REDIS_HOST = os.getenv("REDIS_HOST")
    REDIS_PORT = int(os.getenv("REDIS_PORT"))
    REDIS_DB = int(os.getenv("REDIS_DB"))
    QR_SECRET = os.getenv("QR_SECRET")
    QR_API_URL = os.getenv("QR_API_URL", "https://api.qrserver.com/v1/create-qr-code/")
    BALE_CHAT_BASE = os.getenv("BALE_CHAT_BASE", "https://web.bale.ai/chat?uid=1322664071")