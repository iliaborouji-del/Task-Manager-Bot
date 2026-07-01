from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from bot.database.models import Base

DATABASE_URL = "sqlite+aiosqlite:///tasks.db"

engine = create_async_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    engine, 
    class_=AsyncSession,
    expire_on_commit=False
)
async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(
            Base.metadata.create_all
        )

async def get_session():
    async with SessionLocal() as session:
        return session