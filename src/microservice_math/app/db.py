import aiosqlite
from app.models import request_log

DB_PATH = "microservice_math.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(request_log.CREATE_TABLE_SQL)
        await db.commit()

async def get_db_connection():
    return await aiosqlite.connect(DB_PATH)