from sqlalchemy import select, update, delete, func
from bot.database.models import Categories, Tasks
from sqlalchemy.ext.asyncio import AsyncSession

# ---------- Create Category ----------
async def create_category(session, user_id: int, name: str):
    category = Categories(
        user_id=user_id,
        name=name,
    )

    session.add(category)
    await session.commit()
    await session.refresh(category)

    return category


# ---------- Get All Categories ----------
async def get_all_categories(session, user_id: int):
    result = await session.execute(
        select(Categories)
        .where(Categories.user_id == user_id)
        .order_by(Categories.name)
    )

    return result.scalars().all()


# ---------- Get Category ----------
async def get_category(session, category_id: int, user_id: int):
    result = await session.execute(
        select(Categories).where(
            Categories.id == category_id,
            Categories.user_id == user_id,
        )
    )

    return result.scalar_one_or_none()


# ---------- Rename Category ----------
async def rename_category(session, category_id: int, user_id: int, new_name: str):
    await session.execute(
        update(Categories)
        .where(
            Categories.id == category_id,
            Categories.user_id == user_id,
        )
        .values(name=new_name)
    )

    await session.commit()


# ---------- Move Tasks ----------
async def move_tasks_to_category(session, old_category_id: int, new_category_id: int, user_id: int):
    await session.execute(
        update(Tasks)
        .where(
            Tasks.user_id == user_id,
            Tasks.category_id == old_category_id,
        )
        .values(category_id=new_category_id)
    )

    await session.commit()


# ---------- Delete Category ----------
async def delete_category(session, category_id: int, user_id: int):
    await session.execute(
        delete(Categories).where(
            Categories.id == category_id,
            Categories.user_id == user_id,
        )
    )

    await session.commit()


# ---------- Count Tasks ----------
async def count_category_tasks(session, category_id: int, user_id: int):
    result = await session.execute(
        select(Tasks).where(
            Tasks.user_id == user_id,
            Tasks.category_id == category_id,
        )
    )

    return len(result.scalars().all())

# ---------- Category Exists ----------
async def category_exists(session, user_id: int, name: str):
    result = await session.execute(
        select(Categories).where(
            Categories.user_id == user_id,
            Categories.name == name,
        )
    )

    return result.scalar_one_or_none() is not None

# ---------- Get Category By Name ----------
async def get_category_by_name(session, user_id: int, name: str):
    result = await session.execute(
        select(Categories).where(
            Categories.user_id == user_id,
            Categories.name == name,
        )
    )

    return result.scalar_one_or_none()

# ---------- Has Tasks ----------
async def category_has_tasks(session, category_id: int, user_id: int):
    return (
        await count_category_tasks(
            session,
            category_id,
            user_id,
        )
    ) > 0
    
async def count_categories(session: AsyncSession, user_id: int) -> int:
    result = await session.scalar(
        select(func.count(Categories.id))
        .where(Categories.user_id == user_id)
    )

    return result or 0

async def get_other_categories(session: AsyncSession, user_id: int, category_id: int) -> list[Categories]:
    result = await session.scalars(
        select(Categories)
        .where(
            Categories.user_id == user_id,
            Categories.id != category_id,
        )
        .order_by(Categories.name)
    )

    return list(result.all())