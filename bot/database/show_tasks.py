from sqlalchemy import select
from bot.database.models import Tasks

async def show_not_completed_tasks(session, user_id: int):
    result = await session.execute(
        select(Tasks).where(
            Tasks.user_id == user_id,
            Tasks.status.in_(["انجام نشده ⭕", "در حال انجام ⏳"])
        )
    )
    return result.scalars().all()