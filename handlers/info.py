from aiogram import Router, F
from aiogram.types import Message

from database.models import AsyncSessionLocal, User
from handlers.membership import check_membership, force_join_keyboard

router = Router()


@router.message(F.text == "👤 مشخصات من")
async def my_profile(message: Message):

    # چک عضویت
    if not await check_membership(message.bot, message.from_user.id):
        await message.answer(
            "⚠️ برای مشاهده مشخصات باید ابتدا در کانال عضو شوید:",
            reply_markup=force_join_keyboard()
        )
        return

    async with AsyncSessionLocal() as session:

        # گرفتن کاربر از دیتابیس
        user = await session.get(User, message.from_user.id)

        # اگر کاربر ثبت نشده بود → ثبتش کن
        if not user:
            new_user = User(
                id=message.from_user.id,
                username=message.from_user.username,
                referred_by=None
            )
            session.add(new_user)
            await session.commit()
            user = new_user

        # نمایش مشخصات
        await message.answer(
            "👤 مشخصات شما:\n\n"
            f"🆔 آیدی عددی: {message.from_user.id}\n"
            f"📛 یوزرنیم: @{message.from_user.username or 'ندارد'}\n"
            f"👥 تعداد رفرال‌های ثبت‌شده: {user.referrals_count}\n"
        )
