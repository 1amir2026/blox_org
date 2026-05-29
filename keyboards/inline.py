from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def design_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="طرح ۱", callback_data="design_1")],
        [InlineKeyboardButton(text="طرح ۲", callback_data="design_2")],
        [InlineKeyboardButton(text="طرح ۳", callback_data="design_3")]
    ])

def light_color_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="نور قرمز", callback_data="light_red")],
        [InlineKeyboardButton(text="نور آبی", callback_data="light_blue")],
        [InlineKeyboardButton(text="نور بنفش", callback_data="light_purple")],
        [InlineKeyboardButton(text="نور سفید", callback_data="light_white")]
    ])

def bg_color_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="پس‌زمینه مشکی", callback_data="bg_black")],
        [InlineKeyboardButton(text="پس‌زمینه آبی تیره", callback_data="bg_darkblue")],
        [InlineKeyboardButton(text="پس‌زمینه بنفش", callback_data="bg_purple")]
    ])