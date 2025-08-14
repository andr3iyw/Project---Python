from datetime import datetime, UTC
import asyncio
import json
from flask import request, jsonify, Flask

app = Flask(__name__)

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS request_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    operation TEXT NOT NULL,
    input_data TEXT NOT NULL,
    result TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    username TEXT NOT NULL
);
"""


INSERT_LOG_SQL = """
INSERT INTO request_log (operation, input_data, result, timestamp, username)
VALUES (?, ?, ?, ?, ?);
"""


FETCH_LOGS_SQL = "SELECT * FROM request_log WHERE username = ? ORDER BY id;"


async def insert_log(db, operation: str, input_data: str, result: str, username: str):
    timestamp = datetime.now(UTC).isoformat()
    print(
        f"[SE INTAMPLA LOGGING] {operation} | {input_data} → {result} @ {timestamp} (user={username})"
    )
    await db.execute(
        INSERT_LOG_SQL, (operation, input_data, result, timestamp, username)
    )
    await db.commit()


def get_username_from_request():
    print("Request headers:", dict(request.headers))
    username = request.headers.get("X-Username", "anonymous")
    print("Extracted username:", username)
    return username



async def log_to_db(operation: str, input_data: dict, result, username: str):
    from gateway.app.db import get_db_connection
    from auth_service.models.request_log import insert_log

    db = await get_db_connection()
    input_json = json.dumps(input_data)
    await insert_log(db, operation, input_json, str(result), username)
    await db.close()