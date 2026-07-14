import os
from dotenv import load_dotenv

load_dotenv()
class Config():
    BOT_TOKEN = os.getenv("TOKEN")
    REDIS_HOST = os.getenv("REDIS_HOST")
    REDIS_PORT = os.getenv("REDIS_PORT")
    REDIS_DB = os.getenv("REDIS_DB")
    QR_SECRET = os.getenv("QR_SECRET")
    BOT_USERNAME = os.getenv("BOT_USERNAME", "tasks_manager_bot")
    QR_API_URL = os.getenv("QR_API_URL", "https://api.qrserver.com/v1/create-qr-code/")
    BALE_CHAT_BASE = os.getenv("BALE_CHAT_BASE", "https://web.bale.ai/chat?uid=1322664071")