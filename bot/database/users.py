from datetime import datetime
from sqlalchemy import select
from bot.database.models import Users
from bot.utils.datetime import now_iran, iran_to_naive

async def get_user(session, user_id: int) -> Users | None:
    result = await session.execute(
        select(Users).where(Users.user_id == user_id)
    )
    return result.scalar_one_or_none()

async def create_user(session, user_id: int, full_name: str, username: str | None) -> Users:
    user = Users(
        user_id = user_id,
        full_name = full_name,
        username = username
    )
    
    session.add(user)
    await session.commit()
    await session.refresh(user)
    
    return user

async def update_last_activity(session, user: Users) -> None:
    user.last_activity = iran_to_naive(now_iran())
    await session.commit()
    
async def register_user(session, user_id: int, full_name: str, username: str | None) -> Users:
    user = await get_user(session, user_id)
    
    if user is None:
        return await create_user(
            session=session,
            user_id=user_id,
            full_name=full_name,
            username=username
        )
    
    if (
        user.full_name != full_name
        or user.username != username
    ):
        user.full_name = full_name
        user.username = username
        
    user.last_activity = iran_to_naive(now_iran())
    
    await session.commit()
    
    return user