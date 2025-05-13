import asyncio
from src.database.database import init_db

async def main():
    """Drops and creates tables in the database"""
    await init_db()

if __name__ == "__main__":
    asyncio.run(main())