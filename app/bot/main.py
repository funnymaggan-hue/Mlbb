import asyncio, logging
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
from app.config import settings
logging.basicConfig(level=logging.INFO)
async def main():
    if not settings.BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN .env ichida sozlanmagan")
    bot=Bot(settings.BOT_TOKEN); dp=Dispatcher()
    @dp.message(CommandStart())
    async def start(message: Message):
        kb=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🏆 Mini App’ni ochish",web_app=WebAppInfo(url=settings.WEBAPP_URL))]])
        await message.answer("MLBB Tournament Pro’ga xush kelibsiz. Turnirlar va jamoalarni Mini App orqali boshqaring.",reply_markup=kb)
    @dp.message(Command("help"))
    async def help_cmd(message: Message):
        await message.answer("/start — Mini App\n/profile — profil\n/tournaments — turnirlar\n/myteam — jamoa\n/mystats — statistika\n/admin — administrator")
    @dp.message(Command("profile"))
    async def profile(message: Message): await message.answer(f"Telegram ID: {message.from_user.id}\nProfil tafsilotlari Mini App’da.")
    @dp.message(Command("tournaments"))
    async def tournaments(message: Message): await message.answer(f"Turnirlarni ko‘rish: {settings.WEBAPP_URL}")
    @dp.message(Command("myteam"))
    async def myteam(message: Message): await message.answer("Jamoangizni Mini App ichidagi Jamoalar bo‘limida boshqaring.")
    @dp.message(Command("mystats"))
    async def mystats(message: Message): await message.answer("Statistika Mini App’da ko‘rsatiladi.")
    @dp.message(Command("admin"))
    async def admin(message: Message):
        if message.from_user.id not in settings.admin_ids: return await message.answer("Ruxsat yo‘q.")
        await message.answer("Administrator API’lari Mini App backendida mavjud.")
    try: await dp.start_polling(bot)
    finally: await bot.session.close()
if __name__ == "__main__": asyncio.run(main())
