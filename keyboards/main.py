from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔗 لینک رفرال")],
        [KeyboardButton(text="❓ سوالات متداول")],
        [KeyboardButton(text="🖼 درخواست پروفایل")],
        [KeyboardButton(text="📞 پشتیبانی")],
        [KeyboardButton(text="👤 مشخصات من")]
    ],
    resize_keyboard=True
)