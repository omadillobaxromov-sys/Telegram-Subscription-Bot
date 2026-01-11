import aiosqlite
from datetime import datetime, timedelta

DB_NAME = "users.db"

# ✅ Bazani yaratish (init_db)
async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            sub_type TEXT,
            duration_days REAL,
            check_image TEXT,
            expires_at TEXT
        )
        """)
        await db.commit()

# ✅ Foydalanuvchini qo‘shish yoki yangilash
async def add_or_update_user(user_id: int, sub_type: str, duration_days: float, check_image: str):
    expires_at = (datetime.now() + timedelta(days=duration_days)).isoformat()
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        INSERT INTO users (user_id, sub_type, duration_days, check_image, expires_at)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            sub_type=excluded.sub_type,
            duration_days=excluded.duration_days,
            check_image=excluded.check_image,
            expires_at=excluded.expires_at
        """, (user_id, sub_type, duration_days, check_image, expires_at))
        await db.commit()

# ✅ Ma'lumotni olish
async def get_user(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cursor:
            return await cursor.fetchone()

# ✅ Obunani tasdiqlash
async def verify_user(user_id: int):
    # Foydalanuvchi bazada mavjudligini tekshirish
    user = await get_user(user_id)
    if user:
        # Foydalanuvchi mavjud, obuna tasdiqlangan
        return True
    return False

# ✅ Obunani rad etish yoki o‘chirish
async def mark_invalid(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        await db.commit()

# ✅ Tugagan obunalarni olish
async def get_expired_users():
    now = datetime.now().isoformat()
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT user_id FROM users WHERE expires_at <= ?", (now,)) as cursor:
            return [row[0] async for row in cursor]

# ✅ Tugagan foydalanuvchini o‘chirish
async def remove_user(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        await db.commit()

# ✅ Barcha foydalanuvchilarni olish (admin/scheduler uchun)
async def get_all_users():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT user_id, expires_at FROM users") as cursor:
            return await cursor.fetchall()
