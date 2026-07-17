import os
from dotenv import load_dotenv

load_dotenv(".env.telegram")  # پیش‌فرض

source = os.getenv("SOURCE", "telegram")

if source == "bale":
    load_dotenv(".env.bale", override=True)
else:
    load_dotenv(".env.telegram", override=True)


class Config:
    SOURCE = source
    BOT_TOKEN = os.getenv("TOKEN")
    API_BASE = os.getenv("API_BASE")

    REDIS_HOST = os.getenv("REDIS_HOST")
    REDIS_PORT = int(os.getenv("REDIS_PORT"))
    REDIS_DB = int(os.getenv("REDIS_DB"))

    QR_SECRET = os.getenv("QR_SECRET")
    QR_API_URL = os.getenv("QR_API_URL")
    BALE_CHAT_BASE = os.getenv("BALE_CHAT_BASE")