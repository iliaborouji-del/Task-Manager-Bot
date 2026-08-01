from sqlalchemy import select, func
from bot.database.models import Users, Tasks, Categories
from datetime import timedelta
from bot.utils.datetime import now_iran, iran_to_naive

async def get_users_count(session) -> int:
    result = await session.execute(
        select(func.count(Users.id))
    )
    
    return result.scalar_one()

async def get_users_page(session, offset: int, limit: int = 10):
    result = await session.execute(
        select(Users)
        .order_by(Users.created_at.desc())
        .offset(offset)
        .limit(limit)
    )

    return result.scalars().all()

async def get_user_by_id(session, user_id: int) -> Users | None:
    result = await session.execute(
        select(Users)
        .where(Users.user_id == user_id)
    )
    
    return result.scalar_one_or_none()

async def get_tasks_count(session) -> int:
    result = await session.execute(
        select(func.count(Tasks.id))
    )
    
    return result.scalar_one()

async def get_categories_count(session) -> int:
    result = await session.execute(
        select(func.count(Categories.id))
    )
    
    return result.scalar_one()

async def get_active_users_count(session) -> int:
    seven_days_ago = iran_to_naive(
        now_iran() - timedelta(days=7)
    )

    result = await session.execute(
        select(func.count(Users.id))
        .where(
            Users.last_activity >= seven_days_ago
        )
    )

    return result.scalar_one()

async def get_new_users_today_count(session) -> int:

    today = now_iran().date()

    result = await session.execute(
        select(func.count(Users.id))
        .where(
            func.date(Users.created_at) == today
        )
    )

    return result.scalar_one()

async def get_blocked_users_count(session) -> int:
    result = await session.execute(
        select(func.count(Users.id))
        .where(
            Users.is_blocked.is_(True)
        )
    )

    return result.scalar_one()

async def get_last_registered_user(session) -> Users | None:
    result = await session.execute(
        select(Users)
        .order_by(Users.created_at.desc())
        .limit(1)
    )

    return result.scalar_one_or_none()

async def get_all_users_ids(session) -> list[int]:
    result = await session.execute(
        select(Users.user_id)
    )

    return result.scalars().all()