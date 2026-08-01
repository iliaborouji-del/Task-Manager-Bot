from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery
from config import Config

class AdminFilter(BaseFilter):
    async def __call__(self, message: Message | CallbackQuery) -> bool:
        return message.from_user.id == Config.ADMIN_ID