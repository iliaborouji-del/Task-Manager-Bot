from bot.database.models import Tasks
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

async def save_task(session, user_id, data):
    deadline = data.get("deadline")

    if isinstance(deadline, str):
        deadline = datetime.fromisoformat(deadline)

    task = Tasks(
        user_id=user_id,
        title=data["title"],
        description=data["description"],
        priority=data["priority"],
        deadline=deadline,
        status=data["status"],
    )

    session.add(task)
    await session.commit()

    logger.info(
        "Task created. id=%s user=%s",
        task.id,
        user_id
    )