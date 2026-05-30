# keyboards/main_reply.py
import os
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

def main_reply_keyboard(user_id: int):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton(text="🖼 درخواست پروفایل"))
    kb.add(KeyboardButton(text="🎁 دعوت و رفرال"))
    kb.add(KeyboardButton(text="ℹ️ راهنما"))

    # فقط برای ادمین دکمه پنل اضافه شود
    if user_id == ADMIN_ID:
        kb.add(KeyboardButton(text="👨🏻‍💻 پنل ادمین"))

    return kb
