import hashlib
from datetime import datetime, UTC

INSERT_USER_SQL = """
INSERT INTO users (username, password_hash, created_at)
VALUES (?, ?, ?);
"""

FETCH_USER_SQL = "SELECT * FROM users WHERE username = ?;"


async def create_user(db, username: str, password: str):
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    created_at = datetime.now(UTC).isoformat()
    await db.execute(INSERT_USER_SQL, (username, password_hash, created_at))
    await db.commit()


async def get_user(db, username: str):
    cursor = await db.execute(FETCH_USER_SQL, (username,))
    return await cursor.fetchone()


async def verify_user(db, username: str, password: str):
    user = await get_user(db, username)
    if not user:
        print(f"verify_user: user '{username}' not found")
        return False
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    result = user[2] == password_hash
    print(f"verify_user: user='{username}', password_match={result}")
    return result
