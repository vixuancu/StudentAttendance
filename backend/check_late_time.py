import asyncio
from src.db.session import get_db
from src.db.models.class_session import ClassSession
from sqlalchemy import select

async def main():
    async for session in get_db():
        result = await session.execute(select(ClassSession).limit(5)) # 
        for row in result.scalars():
            print(f"Session ID: {row.id}")
            print(f"Session Date: {row.session_date}, type: {type(row.session_date)}")
            print(f"Start Time: {row.start_time}, type: {type(row.start_time)}")
            print(f"Late Time: {row.late_time}, type: {type(row.late_time)}")
        break

if __name__ == "__main__":
    asyncio.run(main())
