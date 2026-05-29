import asyncio
import os

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from handlers.start import router as start_router
from handlers.profile import router as profile_router
from handlers.referral import router as referral_router
from handlers.faq import router as faq_router
from handlers.support import router as support_router

from database.models import init_db

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Router ها
dp.include_router(start_router)
dp.include_router(profile_router)
dp.include_router(referral_router)
dp.include_router(faq_router)
dp.include_router(support_router)


async def main():

    # ساخت دیتابیس
    await init_db()

    print("✅ Bot Started")

    # اجرای ربات
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())