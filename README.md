# Telegram Subscription Bot

Bu bot orqali foydalanuvchilar pullik obuna bo'lishlari va maxfiy kanalga kirishlari mumkin.

## Funksiyalar

- ✅ Foydalanuvchilar obuna turini tanlash (1 oy, 3 oy, 6 oy)
- ✅ To'lov chekini yuborish va admin tomonidan tekshirilishi
- ✅ Avtomatik taklif havolasi yaratish va yuborish
- ✅ Obuna muddati tugagan foydalanuvchilarni avtomatik olib tashlash

## O'rnatish

### 1. Repositoryni klonlash

```bash
git clone <repository_url>
cd "TG bot yaratish"
```

### 2. Virtual environment yaratish

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# yoki
venv\Scripts\activate  # Windows
```

### 3. Kerakli paketlarni o'rnatish

```bash
pip install -r requirements.txt
```

### 4. Konfiguratsiya

`.env.example` faylini `.env` ga ko'chiring va quyidagi ma'lumotlarni to'ldiring:

```bash
cp .env.example .env
```

`.env` faylini tahrirlang:

```
BOT_TOKEN=your_bot_token_here
ADMIN_IDS=123456789
CHANNEL_ID=-1001234567890
CHANNEL_LINK=https://t.me/your_channel
```

### 5. Botni ishga tushirish

```bash
python bot.py
```

## Render.com da deploy qilish

1. Render.com ga kirib, yangi "Web Service" yaratishingiz kerak emas. O'rniga "Background Worker" yoki "Web Service" tanlang.

2. Repositoryni ulang.

3. Environment Variables qo'shing:
   - `BOT_TOKEN` - Bot token
   - `ADMIN_IDS` - Admin IDlar (vergul bilan ajratilgan)
   - `CHANNEL_ID` - Kanal ID
   - `CHANNEL_LINK` - Kanal havolasi (ixtiyoriy)

4. Build Command: `pip install -r requirements.txt`

5. Start Command: `python bot.py`

**Muhim**: Render.com da "Web Service" tanlasangiz, port ochish kerak. Agar "Background Worker" tanlasangiz, bot polling rejimida ishlaydi.

## Foydalanish

1. Botga `/start` buyrug'ini yuboring
2. "🛒 Obuna bo'lish" tugmasini bosing
3. Obuna turini tanlang
4. To'lov chekini (rasm) yuboring
5. Admin tasdiqlagandan keyin kanalga kirish havolasini olasiz

## Admin buyruqlari

- `/myid` - O'z chat IDingizni bilish uchun

## Texnik detallar

- **Framework**: aiogram 3.4.1
- **Database**: SQLite (aiosqlite)
- **Python**: 3.8+
