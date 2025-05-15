from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.database import AsyncSessionLocal


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            raise