from aiogram import Router, F
from aiogram.types import Message

router = Router()

ADMIN_ID = 5508686165


@router.message(F.document & F.reply_to_message)
async def admin_send_result(message: Message):

    if message.from_user.id != ADMIN_ID:
        return

    try:
        text = message.reply_to_message.caption
        user_id = int(text.split("👤 کاربر: ")[1].split("\n")[0])

        await message.bot.send_document(
            user_id,
            message.document.file_id,
            caption="📦 پروفایل نهایی شما آماده شد!"
        )

        await message.answer("✅ فایل برای کاربر ارسال شد.")

    except:
        await message.answer("❌ خطا در ارسال فایل.")
