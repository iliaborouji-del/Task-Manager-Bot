from sqlalchemy import select
from bot.database.models import Tasks

async def get_all_tasks(session, user_id: int):
    result = await session.execute(
        select(Tasks).where(Tasks.user_id == user_id).order_by(Tasks.id.desc())
    )
    return result.scalars().all()