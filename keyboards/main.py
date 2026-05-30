# keyboards/main.py
import os
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

def main_menu(user_id: int):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)

    kb.add(KeyboardButton(text="🖼 درخواست پروفایل"))
    kb.add(KeyboardButton(text="🔗 لینک رفرال"))
    kb.add(KeyboardButton(text="👤 مشخصات من"))
    kb.add(KeyboardButton(text="❓ سوالات متداول"))
    kb.add(KeyboardButton(text="📞 پشتیبانی"))

    # فقط برای ادمین
    if user_id == ADMIN_ID:
        kb.add(KeyboardButton(text="👨🏻‍💻 پنل ادمین"))

    return kb
