from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from bot.database.models import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager

DATABASE_URL = "sqlite+aiosqlite:///tasks.db"
SYNC_DATABASE_URL = "sqlite:///tasks.db"

engine = create_async_engine(DATABASE_URL, echo=False)

sync_engine = create_engine(
    SYNC_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = async_sessionmaker(
    engine, 
    expire_on_commit=False
)

SyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine
)

async def get_session():
    return SessionLocal()

def get_session_sync():
    return SyncSessionLocal()
    
async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
@asynccontextmanager
async def session_scope():
    session: AsyncSession = SessionLocal()
    try:
        yield session
    finally:
        await session.close()