from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from bot.database.models import Base

DATABASE_URL = "sqlite+aiosqlite:///tasks.db"

engine = create_async_engine(DATABASE_URL, echo=False)

SessionLocal = async_sessionmaker(
    engine, 
    expire_on_commit=False
)

async def get_session():
    return SessionLocal()
    
async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)