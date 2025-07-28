import pytest
import asyncio
import json
from app.main import create_app
from app.db import get_db_connection

@pytest.fixture
def client():
    app = create_app()
    app.testing = True
    return app.test_client()

def test_factorial_logging(client):
    response = client.get("/math/factorial?n=5")
    assert response.status_code == 200
    data = response.get_json()
    assert data["result"] == 120

    async def fetch_log():
        db = await get_db_connection()
        async with db.execute(
            "SELECT operation, input_data, result FROM request_log ORDER BY id DESC LIMIT 1"
        ) as cursor:
            row = await cursor.fetchone()
        await db.close()
        return row

    row = asyncio.run(fetch_log())
    assert row[0] == "factorial"
    assert json.loads(row[1]) == {"n": 5}
    assert row[2] == "120"

def test_pow_logging(client):
    response = client.get("/math/pow?base=2&exp=4")
    assert response.status_code == 200
    data = response.get_json()
    assert data["result"] == 16

    async def fetch_log():
        db = await get_db_connection()
        async with db.execute(
            "SELECT operation, input_data, result FROM request_log ORDER BY id DESC LIMIT 1"
        ) as cursor:
            row = await cursor.fetchone()
        await db.close()
        return row

    row = asyncio.run(fetch_log())
    assert row[0] == "pow"
    assert json.loads(row[1]) == {"base": 2.0, "exp": 4.0}
    assert float(row[2]) == 16.0

def test_fibonacci_logging(client):
    response = client.get("/math/fibonacci?n=7")
    assert response.status_code == 200
    data = response.get_json()
    assert data["result"] == 13

    async def fetch_log():
        db = await get_db_connection()
        async with db.execute(
            "SELECT operation, input_data, result FROM request_log ORDER BY id DESC LIMIT 1"
        ) as cursor:
            row = await cursor.fetchone()
        await db.close()
        return row

    row = asyncio.run(fetch_log())
    assert row[0] == "fibonacci"
    assert json.loads(row[1]) == {"n": 7}
    assert row[2] == "13"