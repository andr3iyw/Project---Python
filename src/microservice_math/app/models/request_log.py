from datetime import datetime, UTC

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS request_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    operation TEXT NOT NULL,
    input_data TEXT NOT NULL,
    result TEXT NOT NULL,
    timestamp TEXT NOT NULL
);
"""


INSERT_LOG_SQL = """
INSERT INTO request_log (operation, input_data, result, timestamp)
VALUES (?, ?, ?, ?);
"""


FETCH_LOGS_SQL = "SELECT * FROM request_log ORDER BY id DESC LIMIT 20;"


async def insert_log(db, operation: str, input_data: str, result: str):
    timestamp = datetime.now(UTC).isoformat()
    print(
        f"[SE INTAMPLA LOGGING] {operation} | {input_data} → {result} @ {timestamp}"
    )
    await db.execute(
        INSERT_LOG_SQL, (operation, input_data, result, timestamp)
    )
    await db.commit()
