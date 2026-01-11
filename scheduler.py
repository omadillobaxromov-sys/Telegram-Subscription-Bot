import asyncio
from datetime import datetime
from aiogram import Bot
from database import get_all_users, mark_invalid
from config import load_config

config = load_config()
CHANNEL_ID = config.CHANNEL_ID

async def check_subscriptions(bot: Bot):
    users = await get_all_users()
    now = datetime.now()

    for user in users:
        user_id, expires_at_str = user
        if expires_at_str:
            try:
                expires_at = datetime.fromisoformat(expires_at_str)
                if expires_at < now:
                    try:
                        await bot.ban_chat_member(chat_id=CHANNEL_ID, user_id=user_id, until_date=0)
                        await bot.unban_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
                        await mark_invalid(user_id)
                        print(f"⏳ Obuna muddati tugadi va {user_id} chiqarildi.")
                    except Exception as e:
                        print(f"⚠️ {user_id} ni chiqarishda xato: {e}")
            except ValueError as e:
                print(f"⚠️ {user_id} uchun muddat formati noto'g'ri: {e}")

async def scheduler_task(bot: Bot):
    while True:
        try:
            await check_subscriptions(bot)
        except Exception as e:
            print(f"⚠️ Jadval tekshiruvda xatolik: {e}")
        await asyncio.sleep(3600)  # 1 soatda 1 marta

def setup_scheduler(bot: Bot):
    # Background task yaratish (main() async funksiyada chaqiriladi, shuning uchun event loop bor)
    asyncio.create_task(scheduler_task(bot))
