from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery
from bot.database.connection import session_scope
from bot.database.users import is_admin

class AdminFilter(BaseFilter):
    async def __call__(self, event: Message | CallbackQuery) -> bool:
        async with session_scope() as session:
            return await is_admin(
                session=session,
                user_id=event.from_user.id,
            )