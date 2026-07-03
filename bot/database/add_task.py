from bot.database.models import Tasks

async def save_task(session, user_id, data):
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