# handlers/admin_commands.py
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import select
import logging

from database.models import AsyncSessionLocal, User

router = Router()
logger = logging.getLogger(__name__)

# **اینجا آی‌دی ادمین را قرار بده** (عدد صحیح)
ADMINS = {5508686165}

@router.message(Command(commands=["whoami"]))
async def whoami_handler(message: Message):
    try:
        await message.reply(f"your id: {message.from_user.id}")
    except Exception as e:
        logger.exception("whoami failed: %s", e)

@router.message(Command(commands=["giveref"]))
async def give_ref_handler(message: Message):
    """
    Usage: /giveref <user_id> <count>
    Example: /giveref 987654321 1
    """
    try:
        sender_id = message.from_user.id
        logger.info("Received /giveref from %s: %s", sender_id, message.text)

        if sender_id not in ADMINS:
            await message.reply("❌ دسترسی ندارید. ابتدا آی‌دی خود را با /whoami بدست بیاور و در ADMINS قرار بده.")
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
                user = User(id=target_id, username=None, referred_by=None, referrals_count=0)
                session.add(user)

            user.referrals_count = (user.referrals_count or 0) + count
            await session.commit()

        await message.reply(f"✅ به کاربر `{target_id}` مقدار `{count}` رفرال اضافه شد.")
        logger.info("Admin %s added %s referrals to %s", sender_id, count, target_id)

    except Exception as e:
        logger.exception("Error in /giveref handler: %s", e)
        try:
            await message.reply("❗ خطا در اجرای دستور. لاگ‌ها را بررسی کن.")
        except Exception:
            logger.exception("Failed to send error reply for /giveref")
