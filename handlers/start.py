from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from keyboards.main import main_menu
from database.models import AsyncSessionLocal, User
from sqlalchemy import select

router = Router()


@router.message(CommandStart())
async def start(message: Message):

    user_id = message.from_user.id

    cursor.execute(
        "INSERT OR IGNORE INTO users (user_id) VALUES (?)",
        (user_id,)
    )
    conn.commit()

    args = message.text.split()

    if len(args) > 1:

        referrer_id = int(args[1])

        if referrer_id != user_id:

            cursor.execute(
                "UPDATE users SET referrals = referrals + 1 WHERE user_id=?",
                (referrer_id,)
            )
            conn.commit()

            await message.answer(
                "🎉 شما با لینک رفرال وارد شدید.",
                reply_markup=main_menu
            )

            try:
                await message.bot.send_message(
                    referrer_id,
                    f"🎉 یک نفر با لینک شما وارد شد.\n\n"
                    f"👤 آیدی:\n{user_id}"
                )
            except:
                pass

    else:
        await message.answer(
            "👋 خوش آمدید",
            reply_markup=main_menu
        )