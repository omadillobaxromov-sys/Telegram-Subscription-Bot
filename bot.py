# bot.py
import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton
)
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import CommandStart, Command
from aiogram.client.default import DefaultBotProperties

from config import load_config
from database import init_db, add_or_update_user, verify_user, mark_invalid
from scheduler import setup_scheduler

config = load_config()
bot = Bot(
    token=config.BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# === HOLATLAR ===
class Form(StatesGroup):
    choosing_plan = State()
    sending_check = State()

# === /start buyruq ===
@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🛒 Obuna bo'lish")]],
        resize_keyboard=True
    )
    await message.answer(
        f"👋 Salom, <b>{message.from_user.full_name}</b>!\n\n"
        "Bu bot orqali maxfiy kanalimizga pullik obuna bo'lishingiz mumkin.\n\n"
        "💳 Karta raqam:\n"
        "2020 2255 0251 5222 Q.Mirzohalil",
        reply_markup=kb
    )

# === OBUNA TANLASH ===
@dp.message(F.text == "🛒 Obuna bo'lish")
async def choose_subscription(message: Message, state: FSMContext):
    plans = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="1 oylik - 25 000 so‘m", callback_data="sub_1")],
        [InlineKeyboardButton(text="3 oylik - 65 000 so‘m", callback_data="sub_3")],
        [InlineKeyboardButton(text="6 oylik - 130 000 so‘m", callback_data="sub_6")],
    ])
    await message.answer("👇 Obuna turini tanlang:", reply_markup=plans)
    await state.set_state(Form.choosing_plan)

@dp.callback_query(F.data.startswith("sub_"))
async def ask_check(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    duration_map = {"sub_1": 30, "sub_3": 90, "sub_6": 180}
    duration = duration_map.get(callback.data)
    if not duration:
        await callback.message.answer("❌ Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.")
        return
    await state.update_data(duration=duration)
    await callback.message.answer("📤 Iltimos, to‘lov cheki (rasm) ni yuboring:")
    await callback.message.answer("💳 karta raqam: 2020 2255 0251 5222 Q.Mirzohalil")
    await state.set_state(Form.sending_check)

# === TO'LOVNI QABUL QILISH ===
@dp.message(Form.sending_check, F.photo)
async def handle_check(message: Message, state: FSMContext):
    data = await state.get_data()
    duration = data.get("duration")
    if not duration:
        await message.answer("❌ Xatolik yuz berdi. Iltimos, qaytadan obuna tanlang.")
        await state.clear()
        return
    
    file_id = message.photo[-1].file_id

    # ✅ Foydalanuvchini bazaga qo‘shamiz
    await add_or_update_user(
        user_id=message.from_user.id,
        sub_type=f"{duration} kun",
        duration_days=duration,
        check_image=file_id
    )

    # ✅ ADMINlarga yuboramiz
    for admin_id in config.ADMIN_IDS:
        try:
            btns = InlineKeyboardMarkup(inline_keyboard=[[ 
                InlineKeyboardButton(text="✅ Qo‘shish", callback_data=f"approve_{message.from_user.id}"),
                InlineKeyboardButton(text="❌ Rad etish", callback_data=f"reject_{message.from_user.id}")
            ]])
            await bot.send_photo(
                chat_id=admin_id,
                photo=file_id,
                caption=f"🧾 Yangi to‘lov cheki\n👤 ID: <code>{message.from_user.id}</code>\n🕒 Muddati: {duration} kun",
                reply_markup=btns
            )
        except Exception as e:
            print(f"⚠️ Admin {admin_id} ga yuborishda xatolik: {e}")

    # ✅ Foydalanuvchiga javob
    await message.answer("✅ Chek yuborildi. Admin tekshiradi va sizga javob beradi.")
    await state.clear()

# === ADMIN JAVOBI: TASDIQLASH ===
@dp.callback_query(F.data.startswith("approve_"))
async def approve_user(callback: CallbackQuery):
    # Admin tekshiruvi
    if callback.from_user.id not in config.ADMIN_IDS:
        await callback.answer("❌ Siz admin emassiz!", show_alert=True)
        return
    
    await callback.answer()
    try:
        user_id = int(callback.data.split("_")[1])
    except (ValueError, IndexError):
        await callback.message.answer("❌ Xatolik: Noto'g'ri format.")
        return
    await verify_user(user_id)

    try:
        # Har bir foydalanuvchi uchun yagona taklif havolasi yaratamiz
        invite_link = await bot.create_chat_invite_link(
            chat_id=config.CHANNEL_ID,
            member_limit=1,  # faqat 1 kishi ishlata oladi
            creates_join_request=False  # tasdiqlashsiz kira oladi
        )

        # Foydalanuvchiga yuboriladi
        await bot.send_message(
            user_id,
            f"✅ Obunangiz tasdiqlandi!\n"
            f"Kanalga kirish uchun quyidagi havolani bosing:\n\n"
            f"{invite_link.invite_link}"
        )

        await callback.message.edit_caption("✅ Tasdiqlandi — foydalanuvchiga 1 martalik havola yuborildi.")
        print(f"✅ {user_id} uchun taklif havolasi yaratildi.")

    except Exception as e:
        print(f"⚠️ Xatolik taklif havolasi yaratishda: {e}")
        await bot.send_message(user_id, "❌ Obunani tasdiqlashda muammo yuz berdi. Iltimos, keyinroq urinib ko‘ring.")

# === ADMIN JAVOBI: RAD ETISH ===
@dp.callback_query(F.data.startswith("reject_"))
async def reject_user(callback: CallbackQuery):
    # Admin tekshiruvi
    if callback.from_user.id not in config.ADMIN_IDS:
        await callback.answer("❌ Siz admin emassiz!", show_alert=True)
        return
    
    await callback.answer()
    try:
        user_id = int(callback.data.split("_")[1])
    except (ValueError, IndexError):
        await callback.message.answer("❌ Xatolik: Noto'g'ri format.")
        return

    try:
        await mark_invalid(user_id)  # Foydalanuvchini bazada "rad etilgan" deb belgilaymiz
        await bot.send_message(
            user_id,
            "❌ Kechirasiz, yuborgan chek rad etildi.\n"
            "Iltimos, to‘lovni tekshirib, qayta urinib ko‘ring."
        )
        await callback.message.edit_caption("❌ Chek rad etildi.")
        print(f"❌ {user_id} foydalanuvchi rad etildi.")
    except Exception as e:
        print(f"⚠️ Rad etishda xatolik: {e}")
        await bot.send_message(
            user_id,
            "❌ Rad etish jarayonida xatolik yuz berdi. Iltimos, keyinroq urinib ko'ring."
        )

# === ADMIN: CHAT ID OLISH ===
@dp.message(Command("myid"))
async def get_my_chat_id(message: Message):
    await message.answer(f"Bu chat ID: <code>{message.chat.id}</code>")

# === BOTNI ISHGA TUSHIRISH ===
async def main():
    logging.basicConfig(level=logging.INFO)
    print("✅ Bot ishga tushdi!")

    await init_db()  # Bazani tayyorlash
    setup_scheduler(bot)  # Obuna muddati tugaganlarni avtomatik olib tashlash

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
