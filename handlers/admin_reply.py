# handlers/admin_reply.py
import re
import logging
from aiogram import Router, F
from aiogram.types import Message

router = Router()
logger = logging.getLogger(__name__)

# اگر می‌خواهی از ENV استفاده کنی، مقداردهی کن؛ در غیر اینصورت عدد ثابت
import os
ADMIN_ID = int(os.getenv("ADMIN_ID", "5508686165"))

# الگوی امن برای استخراج user id از کپشن: "👤 کاربر: 12345"
USER_ID_RE = re.compile(r"👤\s*کاربر[:\s]*([0-9]+)")

@router.message(F.reply_to_message)
async def admin_reply_handler(message: Message):
    # فقط ادمین مجاز است
    if message.from_user.id != ADMIN_ID:
        return

    orig = message.reply_to_message
    text_to_search = ""
    if orig.caption:
        text_to_search += orig.caption + "\n"
    if orig.text:
        text_to_search += orig.text + "\n"

    m = USER_ID_RE.search(text_to_search)
    if not m:
        await message.reply("❗ شناسه کاربر در پیام سفارش پیدا نشد. مطمئن شو کپشن شامل '👤 کاربر: <id>' هست.")
        logger.warning("admin reply: user id not found. orig_caption=%s orig_text=%s", orig.caption, orig.text)
        return

    user_id = int(m.group(1))

    try:
        # ارسال انواع محتوا به کاربر بر اساس نوع پیام ادمین
        if message.document:
            await message.bot.send_document(chat_id=user_id, document=message.document.file_id, caption=message.caption or None)
        elif message.photo:
            await message.bot.send_photo(chat_id=user_id, photo=message.photo[-1].file_id, caption=message.caption or None)
        elif message.video:
            await message.bot.send_video(chat_id=user_id, video=message.video.file_id, caption=message.caption or None)
        elif message.audio:
            await message.bot.send_audio(chat_id=user_id, audio=message.audio.file_id, caption=message.caption or None)
        elif message.voice:
            await message.bot.send_voice(chat_id=user_id, voice=message.voice.file_id, caption=message.caption or None)
        elif message.sticker:
            await message.bot.send_sticker(chat_id=user_id, sticker=message.sticker.file_id)
        elif message.text:
            await message.bot.send_message(chat_id=user_id, text=message.text)
        else:
            # fallback: forward original admin message to user
            await message.bot.forward_message(chat_id=user_id, from_chat_id=message.chat.id, message_id=message.message_id)

        await message.reply("✅ پاسخ شما به کاربر ارسال شد.")
        logger.info("Admin reply forwarded to user %s by admin %s", user_id, message.from_user.id)

    except Exception as e:
        logger.exception("Error forwarding admin reply: %s", e)
        await message.reply("❌ خطا در ارسال پیام به کاربر. ممکن است کاربر ربات را بلاک کرده باشد یا خطای دیگری رخ داده باشد.")
