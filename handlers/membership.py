from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

CHANNEL_ID = -1002375083668

def force_join_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 عضویت در کانال", url="https://t.me/BloxyDesign")],
        [InlineKeyboardButton(text="✔️ تایید عضویت", callback_data="check_join")]
    ])

async def check_membership(bot, user_id: int):
    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status not in ["left", "kicked"]
    except:
        return False
