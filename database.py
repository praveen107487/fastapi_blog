from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from config import settings

# Active asynchronous connection pipe engine instance
engine = create_async_engine(
    settings.database_url
)

# Workspace session pipeline generation factor context rules
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db():
    """
    Yields transactional workspace boundaries safely via FastAPI Depends scopes.
    """
    async with AsyncSessionLocal() as session:
        yield session


async def init_db():
    """
    Asynchronously synchronizes table structural objects to SQLite cleanly.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)