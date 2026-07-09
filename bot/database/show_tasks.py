from sqlalchemy import select
from bot.database.models import Tasks

async def show_not_done_tasks(session, user_id: int):
    result = await session.execute(select(Tasks).where(
            Tasks.user_id == user_id,
            Tasks.status == "انجام نشده ⭕"
    ))
    return result.scalars().all()

async def show_doing_tasks(session, user_id: int):
    result = await session.execute(
        select(Tasks).where(
            Tasks.user_id == user_id,
            Tasks.status == "در حال انجام ⏳"
        )
    )
    return result.scalars().all()