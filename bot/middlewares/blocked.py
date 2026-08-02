from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from typing import Callable, Dict, Any, Awaitable
from bot.database.connection import session_scope
from bot.database.users import get_user


class BlockedUserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[
            [Any, Dict[str, Any]],
            Awaitable[Any]
        ],
        event: Message | CallbackQuery,
        data: Dict[str, Any],
    ):

        user_id = event.from_user.id

        async with session_scope() as session:

            user = await get_user(
                session=session,
                user_id=user_id,
            )

            if user and user.is_blocked:
                if isinstance(event, Message):
                    await event.answer(
                        "🚫 دسترسی شما به ربات مسدود شده است."
                    )
                elif isinstance(event, CallbackQuery):
                    await event.answer(
                        "🚫 دسترسی شما مسدود شده است.",
                        show_alert=True
                    )

                return

        return await handler(event, data)