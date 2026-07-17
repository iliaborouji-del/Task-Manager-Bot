import os
from dotenv import load_dotenv

source = os.environ.get("SOURCE")

if source == "telegram":
    load_dotenv(".env.telegram")
elif source == "bale":
    load_dotenv(".env.bale")
else:
    raise RuntimeError("Environment variable SOURCE must be set to 'telegtam' ot 'bale'")

class Config:
    SOURCE = source
    BOT_TOKEN = os.getenv("TOKEN")
    API_BASE = os.getenv("API_BASE")
    BALE_CHAT_BASE = os.getenv("BALE_CHAT_BASE")
    TELEGRAM_CHAT_BASE = os.getenv("TELEGRAM_CHAT_BASE")

    REDIS_HOST = os.getenv("REDIS_HOST")
    REDIS_PORT = int(os.getenv("REDIS_PORT"))
    REDIS_DB = int(os.getenv("REDIS_DB"))

    QR_SECRET = os.getenv("QR_SECRET")
    QR_API_URL = os.getenv("QR_API_URL")