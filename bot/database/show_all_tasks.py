from sqlalchemy import select
from bot.database.models import Tasks
from sqlalchemy.orm import selectinload


async def get_all_tasks(session, user_id: int, category_id: int):
    result = await session.execute(
        select(Tasks)
        .options(
            selectinload(Tasks.category)
        )
        .where(
            Tasks.user_id == user_id,
            Tasks.category_id == category_id,
        )
    )

    return result.scalars().all()