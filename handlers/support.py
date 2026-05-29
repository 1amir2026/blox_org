from aiogram import Router, F
from aiogram.types import Message

router = Router()

# آیدی عددی ادمین
ADMIN_ID = 5508686165

waiting_support = {}


@router.message(F.text == "📞 پشتیبانی")
async def support_start(message: Message):

    waiting_support[message.from_user.id] = True

    await message.answer(
        "✍️ پیام خود را ارسال کنید:"
    )


@router.message()
async def support_message(message: Message):

    user_id = message.from_user.id

    # پیام کاربر برای پشتیبانی
    if user_id in waiting_support:

        waiting_support.pop(user_id)

        text = f"""
📩 پیام جدید پشتیبانی

👤 آیدی:
{user_id}

💬 پیام:
{message.text}
"""

        await message.bot.send_message(
            ADMIN_ID,
            text
        )

        await message.answer(
            "✅ پیام شما برای پشتیبانی ارسال شد."
        )

    # پاسخ ادمین
    elif user_id == ADMIN_ID and message.reply_to_message:

        try:

            replied_text = message.reply_to_message.text

            target_id = int(
                replied_text.split("👤 آیدی:\n")[1].split("\n")[0]
            )

            await message.bot.send_message(
                target_id,
                f"📩 پاسخ پشتیبانی:\n\n{message.text}"
            )

            await message.answer("✅ پاسخ ارسال شد.")

        except:
            pass