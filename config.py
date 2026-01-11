from dotenv import load_dotenv
import os
import sys

def load_config():
    load_dotenv()
    
    bot_token = os.getenv("BOT_TOKEN")
    admin_ids = os.getenv("ADMIN_IDS")
    channel_id = os.getenv("CHANNEL_ID")
    channel_link = os.getenv("CHANNEL_LINK")
    
    if not bot_token:
        print("❌ Xatolik: BOT_TOKEN topilmadi! .env faylini tekshiring.")
        sys.exit(1)
    
    if not admin_ids:
        print("❌ Xatolik: ADMIN_IDS topilmadi! .env faylini tekshiring.")
        sys.exit(1)
    
    if not channel_id:
        print("❌ Xatolik: CHANNEL_ID topilmadi! .env faylini tekshiring.")
        sys.exit(1)
    
    try:
        admin_ids_list = [int(admin_id.strip()) for admin_id in admin_ids.split(",")]
        channel_id_int = int(channel_id.strip())
    except ValueError as e:
        print(f"❌ Xatolik: ADMIN_IDS yoki CHANNEL_ID noto'g'ri format! {e}")
        sys.exit(1)
    
    return type("Config", (), {
        "BOT_TOKEN": bot_token.strip(),
        "ADMIN_IDS": admin_ids_list,
        "CHANNEL_ID": channel_id_int,
        "CHANNEL_LINK": channel_link.strip() if channel_link else ""
    })()
