import aiosqlite
from app.models import request_log
from app.models.user_sql import CREATE_USER_TABLE_SQL

DB_PATH = "microservice_math.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(request_log.CREATE_TABLE_SQL)
        await db.execute(CREATE_USER_TABLE_SQL)
        await db.commit()

async def get_db_connection():
    return await aiosqlite.connect(DB_PATH)