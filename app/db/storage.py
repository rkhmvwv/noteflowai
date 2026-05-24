import asyncpg
from datetime import datetime
 
DATABASE_URL = "postgresql://admin:1234@localhost:5432/noteflow"
 
_pool = None
 
 
async def init_db():
    global _pool
    try:
        print("Подключение к PostgreSQL...")
        _pool = await asyncpg.create_pool(DATABASE_URL)
        print("PostgreSQL подключен")
        async with _pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS notes (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL DEFAULT '',
                    created_at TIMESTAMP,
                    title TEXT,
                    description TEXT,
                    concepts TEXT[],
                    key_points TEXT[],
                    important TEXT[],
                    summary TEXT
                )
            """)
            
            await conn.execute("""
                ALTER TABLE notes
                ADD COLUMN IF NOT EXISTS user_id TEXT NOT NULL DEFAULT ''
            """)
        print("Таблица notes готова")
    except Exception as e:
        print("ОШИБКА БД:", e)
        raise
 
 
async def db_save(user_id: str, job_id: str, note: dict):
    async with _pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO notes (
                id, user_id, created_at, title, description,
                concepts, key_points, important, summary
            )
            VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9)
            ON CONFLICT (id) DO NOTHING
            """,
            job_id,
            user_id,
            datetime.now(),
            note.get("title") or "Без названия",
            note.get("description") or "",
            note.get("concepts") or [],
            note.get("key_points") or [],
            note.get("important") or [],
            note.get("summary") or "",
        )
 
 
async def db_list(user_id: str):
    async with _pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM notes WHERE user_id=$1 ORDER BY created_at DESC LIMIT 100",
            user_id
        )
        return [dict(row) for row in rows]
 
 
async def db_delete(user_id: str, job_id: str):
    async with _pool.acquire() as conn:
        result = await conn.execute(
            "DELETE FROM notes WHERE id=$1 AND user_id=$2",
            job_id, user_id
        )
        return result != "DELETE 0"