from aiogram import Router, F
from aiogram.types import Message

from database import cursor

router = Router()


@router.message(F.text == "👤 مشخصات من")
async def profile(message: Message):

    cursor.execute(
        "SELECT referrals FROM users WHERE user_id=?",
        (message.from_user.id,)
    )

    referrals = cursor.fetchone()[0]

    text = f"""
👤 مشخصات شما

🆔 آیدی: {message.from_user.id}

👥 تعداد رفرال: {referrals}

🎁 جوایز فعال:

{"✅ والپیپر آزاد شد" if referrals >= 5 else "❌ والپیپر قفل"}

{"✅ طرح 1 آزاد شد" if referrals >= 3 else "❌ طرح 1 قفل"}

{"✅ طرح 2 آزاد شد" if referrals >= 3 else "❌ طرح 2 قفل"}

{"✅ طرح 3 آزاد شد" if referrals >= 3 else "❌ طرح 3 قفل"}
"""

    await message.answer(text)