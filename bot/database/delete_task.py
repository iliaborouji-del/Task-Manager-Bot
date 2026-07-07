from sqlalchemy import select
from bot.database.models import Tasks

async def delete_task_by_id(session, task_id):
    result = await session.execute(select(Tasks).where(
        Tasks.id == task_id
    ))
    task = result.scalar_one_or_none()
    if task:
        await session.delete(task)
        await session.commit()
