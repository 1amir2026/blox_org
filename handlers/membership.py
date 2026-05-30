from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

CHANNEL_ID = -1002100624495   # کانال تست جدید

def force_join_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 عضویت در کانال", url="https://t.me/ghjusfghjkiuythy654rew")],
        [InlineKeyboardButton(text="✔️ تایید عضویت", callback_data="check_join")]
    ])

async def check_membership(bot, user_id: int):
    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status not in ["left", "kicked"]
    except:
        return False
