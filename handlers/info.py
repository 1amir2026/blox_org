# handlers/info.py

from aiogram import Router, F
from aiogram.types import Message

from database.models import AsyncSessionLocal, User

router = Router()

@router.message(F.text == "👤 مشخصات من")
async def my_profile(message: Message):
    async with AsyncSessionLocal() as session:
        user = await session.get(User, message.from_user.id)

        if not user:
            await message.answer("❌ شما هنوز در سیستم ثبت نشده‌اید.")
            return

        await message.answer(
            "👤 مشخصات شما:\n\n"
            f"🆔 آیدی عددی: {message.from_user.id}\n"
            f"📛 یوزرنیم: @{message.from_user.username or 'ندارد'}\n"
            f"👥 تعداد رفرال‌های ثبت‌شده: {user.referrals_count}\n"
        )
