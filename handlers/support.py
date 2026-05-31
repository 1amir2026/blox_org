from aiogram import Router, F
from aiogram.types import Message

router = Router()

ADMIN_ID = 5508686165
waiting_support = {}


@router.message(F.text == "📞 پشتیبانی")
async def support_start(message: Message):
    waiting_support[message.from_user.id] = True
    await message.answer("✍️ پیام خود را ارسال کنید:")


@router.message(
    F.text &
    ~F.text.in_([
        "🔗 لینک رفرال",
        "❓ سوالات متداول",
        "🖼 درخواست پروفایل",
        "📞 پشتیبانی",
        "👤 مشخصات من"
    ])
)
async def support_message(message: Message):
    user_id = message.from_user.id

    # کاربر پیام پشتیبانی می‌فرستد
    if user_id in waiting_support:
        waiting_support.pop(user_id)

        text = (
            "📩 پیام جدید پشتیبانی\n\n"
            f"👤 کاربر: {user_id}\n\n"
            f"💬 پیام:\n{message.text}"
        )

        await message.bot.send_message(ADMIN_ID, text)
        await message.answer("✅ پیام شما برای پشتیبانی ارسال شد.")
        return

    # ادمین در حال پاسخ دادن است
    if user_id == ADMIN_ID and message.reply_to_message:
        try:
            replied_text = message.reply_to_message.text
            target_id = int(replied_text.split("👤 کاربر: ")[1].split("\n")[0])

            await message.bot.send_message(
                target_id,
                f"📩 پاسخ پشتیبانی:\n\n{message.text}"
            )

            await message.answer("✅ پاسخ ارسال شد.")
        except Exception:
            await message.answer("❗ شناسه کاربر در پیام پیدا نشد.")
