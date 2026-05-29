from aiogram import Router, F
from aiogram.types import Message

from database import cursor

router = Router()


@router.message(F.text == "🔗 لینک رفرال")
async def referral(message: Message):

    bot_username = (await message.bot.get_me()).username

    link = f"https://t.me/{bot_username}?start={message.from_user.id}"

    cursor.execute(
        "SELECT referrals FROM users WHERE user_id=?",
        (message.from_user.id,)
    )

    referrals = cursor.fetchone()[0]

    text = f"""
🔗 لینک رفرال شما:

{link}

👥 تعداد رفرال: {referrals}

🎨 والپیپر: 5 رفرال
🖼 طرح 1: 3 رفرال
🖼 طرح 2: 3 رفرال
🖼 طرح 3: 3 رفرال
"""

    await message.answer(text)