from datetime import datetime
from sqlalchemy import select
from bot.database.models import Users
from bot.utils.datetime import now_iran, iran_to_naive
from bot.database.categories import create_default_category

async def get_user(session, user_id: int) -> Users | None:
    result = await session.execute(
        select(Users).where(Users.user_id == user_id)
    )
    return result.scalar_one_or_none()

async def create_user(session, user_id: int, full_name: str, username: str | None) -> Users:
    user = Users(
        user_id=user_id,
        full_name=full_name,
        username=username
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
    
    await create_default_category(
            session=session,
            user_id=user_id,
        )
        
    user.last_activity = iran_to_naive(now_iran())
    
    await session.commit()
    
    return user

async def set_admin(session, user: Users, value: bool) -> None:
    user.is_admin = value
    await session.commit()

async def set_premium(session, user: Users, value: bool) -> None:
    user.is_premium = value
    await session.commit()

async def is_admin(session, user_id: int) -> bool:
    user = await get_user(session, user_id)

    if user is None:
        return False

    return user.is_admin

async def is_premium(session, user_id: int) -> bool:
    user = await get_user(session, user_id)

    if user is None:
        return False

    return user.is_premium

async def create_owner_admin(session, owner_id: int):
    user = await get_user(
        session,
        owner_id
    )

    if user:
        return

    user = Users(
        user_id=owner_id,
        full_name="Owner",
        is_admin=True,
    )

    session.add(user)

    await session.commit()