from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔗 لینک رفرال")],
        [KeyboardButton(text="👤 مشخصات من")],
        [KeyboardButton(text="❓ سوالات متداول")],
        [KeyboardButton(text="🖼 درخواست پروفایل")],
        [KeyboardButton(text="📞 پشتیبانی")]
    ],
    resize_keyboard=True
)