from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🖼 درخواست پروفایل")],
        [KeyboardButton(text="🔗 لینک رفرال")],
        [KeyboardButton(text="👤 مشخصات من")],
        [KeyboardButton(text="❓ سوالات متداول")],
        [KeyboardButton(text="📞 پشتیبانی")],
 ],
    resize_keyboard=True
)