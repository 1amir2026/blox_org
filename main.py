import asyncio
import os

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from handlers.start import router as start_router
from handlers.profile import router as profile_router
from handlers.referral import router as referral_router
from handlers.faq import router as faq_router
from handlers.support import router as support_router
from handlers.info import router as info_router
from handlers.admin_reply import router as admin_reply_router
from handlers.admin_commands import router as admin_commands_router
from handlers.admin_panel import router as admin_panel_router
from keyboards.main import main_menu
from middlewares.antispam import AntiSpamMiddleware


load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

dp.include_router(start_router)
dp.include_router(admin_panel_router)   # ← بیار بالا
dp.include_router(admin_reply_router)
dp.include_router(admin_commands_router)
dp.include_router(profile_router)
dp.include_router(referral_router)
dp.include_router(faq_router)
dp.include_router(support_router)
dp.include_router(info_router)
dp.message.middleware(AntiSpamMiddleware(limit=0.7))

async def main():
    print("✅ ربات روشن شد...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())