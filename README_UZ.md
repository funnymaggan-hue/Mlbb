# MLBB Tournament Pro — Termux va Railway qo‘llanmasi

## 1. Termux paketlari
Termux’ni yangilang va Python/Git/ZIP vositalarini o‘rnating:
```bash
pkg update -y && pkg upgrade -y
pkg install python git unzip
```

## 2. ZIP’ni ochish
Yuklangan `MLBB-Tournament-Pro.zip` faylini telefonning Download papkasidan loyiha papkasiga ko‘chiring yoki Termux’da quyidagidan foydalaning:
```bash
mkdir -p ~/projects && cd ~/projects
unzip ~/storage/downloads/MLBB-Tournament-Pro.zip
cd MLBB-Tournament-Pro
```
Agar Android xotirasiga ruxsat berilmagan bo‘lsa, avval `termux-setup-storage` buyrug‘ini bajaring.

## 3. Virtual muhit va kutubxonalar
```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 4. .env sozlash
```bash
cp .env.example .env
nano .env
```
Quyidagilarni to‘ldiring:
- `APP_SECRET_KEY`: uzun, tasodifiy maxfiy kalit.
- `BOT_TOKEN`: BotFather bergan token.
- `ADMIN_IDS`: aynan ikkita Telegram raqami, masalan `111111111,222222222`.
- `TELEGRAM_BOT_USERNAME`: bot username’i.
- `WEBAPP_URL`: HTTPS Mini App manzili.
- `DATABASE_URL`: mahalliy test uchun `sqlite+aiosqlite:///./mlbb_tournament.db`; Railway’da `postgresql+asyncpg://...` formatidagi ulanish.

Bot tokenini GitHub’ga yubormang. `.env` `.gitignore` ichida.

## 5. Ma’lumotlar bazasi
Mahalliy SQLite uchun ilova jadvallarni birinchi ishga tushishda yaratadi. Migratsiyalarni tekshirish uchun:
```bash
alembic upgrade head
```
Hozircha boshlang‘ich Alembic revision fayli yaratilmagan bo‘lsa, birinchi revision yarating:
```bash
alembic revision --autogenerate -m "initial schema"
alembic upgrade head
```
Railway’da PostgreSQL service yarating va `DATABASE_URL` qiymatini `postgresql+asyncpg://...` shaklida sozlang.

## 6. Testlar
```bash
pytest -q
python -m compileall -q app
```

## 7. Backendni ishga tushirish
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```
Brauzerda `http://127.0.0.1:8000/health` manzilini tekshiring. Telefonning o‘zida `http://127.0.0.1:8000` interfeysni ko‘rsatadi, ammo Telegram Mini App autentifikatsiyasi uchun HTTPS va Telegram ichidan ochish kerak.

## 8. Telegram botni ishga tushirish
Boshqa Termux sessiyasida:
```bash
cd ~/projects/MLBB-Tournament-Pro
source .venv/bin/activate
python -m app.bot.main
```
`/start` Mini App tugmasini chiqaradi. `WEBAPP_URL` haqiqiy HTTPS manzilga yo‘naltirilgan bo‘lishi shart.

## 9. Railway va GitHub
1. Loyihani GitHub repository’ga yuklang; `.env` va ma’lumotlar bazasi fayllarini qo‘shmang.
2. Railway’da repository’dan service yarating va PostgreSQL qo‘shing.
3. Variables bo‘limida `DATABASE_URL`, `APP_SECRET_KEY`, `BOT_TOKEN`, `ADMIN_IDS`, `WEBAPP_URL` ni sozlang.
4. `railway.json` health-check uchun `/health` ishlatadi. Start buyrug‘i migratsiyadan so‘ng Uvicorn’ni ishga tushiradi.
5. Railway bergan HTTPS domenini `WEBAPP_URL` sifatida belgilang.

## 10. Loglar va nosozliklar
- API health: `/health`
- Railway: Deployments → Logs.
- Termux: xato matni ko‘rinadigan terminal oynasini tekshiring.
- Kutubxona xatosi: `pip install -r requirements.txt`.
- Bot tokeni xatosi: `.env` ichidagi `BOT_TOKEN` ni tekshiring.
- 401: Mini App Telegram ichida ochilganini va `X-Telegram-Init-Data` yuborilayotganini tekshiring.
- MLBB tekshiruvi `pending_review` bo‘lsa, ishonchli provayder sozlanmagan bo‘lishi mumkin.

## MLBB ID haqiqiyligi haqida
ID va server formatini tekshirish akkaunt mavjudligini isbotlamaydi. Ushbu paketda Moonton rasmiy API’si borligi tasdiqlanmagan va provayder kaliti kiritilmagan. Shu sababli tizim o‘yinchini soxta tarzda avtomatik tasdiqlamaydi. Ishonchli provayder topilsa, uning hujjatlari, foydalanish shartlari va javob sxemasi tekshirilgandan keyingina integratsiya qiling.

## Joriy funksional chegaralar
Turnirlar ro‘yxati, jamoa yaratish, jamoa sardori orqali ariza yuborish, MLBB tekshiruv arizasi, admin turnir yaratishi va tekshiruv arizalarini ko‘rishi/tasdiqlashi mavjud. Avtomatik bracket, natijadan reyting hisoblash, jamoa takliflari, to‘liq bildirishnoma worker’i, reklama boshqaruv API’si va to‘liq rus/ingliz tarjimalari hali to‘liq tugallanmagan.
