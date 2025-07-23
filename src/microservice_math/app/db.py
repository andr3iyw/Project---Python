
import aiosqlite
from app.models import request_log
from fastapi import FastAPI, Request
from pydantic import BaseModel
import uvicorn

DB_PATH = "microservice_math.db"

app = FastAPI()

class LogEntry(BaseModel):
    operation: str
    input_data: str
    result: str

@app.on_event("startup")
async def startup():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(request_log.CREATE_TABLE_SQL)
        await db.commit()

@app.post("/log")
async def log_entry(entry: LogEntry):
    async with aiosqlite.connect(DB_PATH) as db:
        await request_log.insert_log(db, entry.operation, entry.input_data, entry.result)
    return {"status": "success"}

if __name__ == "__main__":
    uvicorn.run("app.db:app", host="0.0.0.0", port=7000, reload=True)