# admin_commands.py
from aiogram import Router
from aiogram.types import Message
from sqlalchemy import select
import logging

from database.models import AsyncSessionLocal, User

router = Router()
logger = logging.getLogger(__name__)

# شناسه‌های تلگرام ادمین‌ها را اینجا قرار بده
ADMINS = {5508686165}  # <-- این را با آی‌دی خودت یا لیست ادمین‌ها جایگزین کن

@router.message(lambda message: message.text and message.text.startswith("/giveref"))
async def give_ref_handler(message: Message):
    """
    Usage:
      /giveref <user_id> <count>
    Example:
      /giveref 987654321 1
    """
    try:
        # دسترسی ادمین
        if message.from_user.id not in ADMINS:
            await message.reply("❌ دسترسی ندارید.")
            return

        parts = message.text.strip().split()
        if len(parts) < 3:
            await message.reply("فرمت درست: /giveref <user_id> <count>")
            return

        try:
            target_id = int(parts[1])
            count = int(parts[2])
        except ValueError:
            await message.reply("شناسه یا تعداد نامعتبر است. باید عدد وارد کنی.")
            return

        async with AsyncSessionLocal() as session:
            result = await session.execute(select(User).where(User.id == target_id))
            user = result.scalar_one_or_none()

            if not user:
                # اگر می‌خواهی کاربر جدید بسازی، فیلدهای لازم را پر کن
                user = User(id=target_id, username=None, referred_by=None, referrals_count=0)
                session.add(user)

            # افزایش کانتر (مطمئن شو فیلد referrals_count وجود دارد)
            user.referrals_count = (user.referrals_count or 0) + count
            await session.commit()

        await message.reply(f"✅ به کاربر `{target_id}` مقدار `{count}` رفرال اضافه شد.")
    except Exception as e:
        logger.exception("Error in /giveref handler: %s", e)
        await message.reply("❗ خطا در اجرای دستور. لاگ‌ها را بررسی کن.")
