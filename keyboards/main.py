# keyboards/main.py
import os
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

def main_menu(user_id: int):
    keyboard = [
        [KeyboardButton(text="🖼 درخواست پروفایل")],
        [KeyboardButton(text="🔗 لینک رفرال")],
        [KeyboardButton(text="👤 مشخصات من")],
        [KeyboardButton(text="❓ سوالات متداول")],
        [KeyboardButton(text="📞 پشتیبانی")],
    ]

    if user_id == ADMIN_ID:
        keyboard.append([KeyboardButton(text="پنل ادمین")])

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )
