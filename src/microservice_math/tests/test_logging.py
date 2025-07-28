import pytest
import asyncio
from app.db import get_db_connection
from app.models.request_log import insert_log, CREATE_TABLE_SQL

@pytest.mark.asyncio
async def test_insert_log():
    db = await get_db_connection()
    await db.execute(CREATE_TABLE_SQL)
    await db.commit()

    await insert_log(db, "factorial", '{"n": 5}', "120")

    async with db.execute(
        "SELECT operation, input_data, result FROM request_log ORDER BY id DESC LIMIT 1"
    ) as cursor:
        row = await cursor.fetchone()

    await db.close()

    assert row == ("factorial", '{"n": 5}', "120")