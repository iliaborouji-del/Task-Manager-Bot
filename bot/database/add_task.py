from bot.database.models import Tasks
from datetime import datetime, timezone

async def save_task(session, user_id, data):
    deadline = data.get("deadline")
    if isinstance(deadline, str):
        try:
            deadline_dt = datetime.strptime(deadline, "Y%-%m-%d  %H:%M").replace(tzinfo=timezone.utc)
        except Exception:
            deadline_dt = None
    else:
        deadline_dt = deadline
            
    task = Tasks(
        user_id=user_id,
        title=data["title"],
        description=data["description"],
        priority=data["priority"],
        deadline=data["deadline"],
        status=data["status"],
    )
    
    session.add(task)
    await session.commit()