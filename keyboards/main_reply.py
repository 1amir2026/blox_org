def main_reply_keyboard(user_id: int):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton(text="🖼 درخواست پروفایل"))
    kb.add(KeyboardButton(text="🎁 دعوت و رفرال"))
    kb.add(KeyboardButton(text="ℹ️ راهنما"))

    if user_id == ADMIN_ID:
        kb.add(KeyboardButton(text="👨🏻‍💻 پنل ادمین"))

    return kb
