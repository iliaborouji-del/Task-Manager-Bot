from sqlalchemy import select
from sqlalchemy.orm import selectinload
from bot.database.models import Tasks

async def show_not_completed_tasks(session, user_id: int, category_id: int):
    result = await session.execute(
        select(Tasks)
        .options(selectinload(Tasks.category))
        .where(
            Tasks.user_id == user_id,
            Tasks.category_id == category_id,
            Tasks.status.in_(
                [
                    "انجام نشده ⭕",
                    "در حال انجام ⏳",
                ]
            ),
        )
        .order_by(Tasks.deadline)
    )

    return result.scalars().all()