from aiogram import Router, F
from aiogram.types import Message

from sqlalchemy import select

from database.models import AsyncSessionLocal, User

router = Router()


@router.message(F.text == "🔗 لینک رفرال")
async def referral(message: Message):

    bot_username = (await message.bot.get_me()).username

    link = f"https://t.me/{bot_username}?start={message.from_user.id}"

    async with AsyncSessionLocal() as session:

        result = await session.execute(
            select(User).where(User.id == message.from_user.id)
        )

        user = result.scalar_one_or_none()

        referrals = user.referrals_count if user else 0

    text = f"""
🔗 لینک رفرال شما:

{link}

👥 تعداد رفرال: {referrals}
"""

    await message.answer(text)