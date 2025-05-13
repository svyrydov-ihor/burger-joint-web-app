from typing import Annotated

from src.database.database import AsyncSessionLocal

async def get_db_session():
    async with AsyncSessionLocal as session:
        try:
            yield session
        finally:
            await session.close()

DbSession = Annotated[AsyncSessionLocal, get_db_session]