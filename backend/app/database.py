import aiosqlite
from pathlib import Path

DATABASE_PATH = Path(__file__).parent.parent / "db.sqlite3"

async def get_db():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        yield db

async def init_db():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS forms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                contact TEXT NOT NULL,
                note TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS coupons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                total INTEGER NOT NULL,
                remaining INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS coupon_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                coupon_id INTEGER NOT NULL,
                grabbed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (coupon_id) REFERENCES coupons(id)
            )
        """)
        # Insert sample coupons if none exist
        cursor = await db.execute("SELECT COUNT(*) FROM coupons")
        count = (await cursor.fetchone())[0]
        if count == 0:
            await db.execute("INSERT INTO coupons (name, total, remaining) VALUES ('新人券 10元', 100, 100)")
            await db.execute("INSERT INTO coupons (name, total, remaining) VALUES ('满减券 20元', 50, 50)")
            await db.execute("INSERT INTO coupons (name, total, remaining) VALUES ('VIP券 50元', 20, 20)")
        await db.commit()