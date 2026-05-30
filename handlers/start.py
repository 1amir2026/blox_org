from aiogram import Router, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select

from keyboards.main import main_menu
from database.models import AsyncSessionLocal, User

router = Router()

# آیدی واقعی کانال BloxyDesign
CHANNEL_ID = -1002375083668


# کیبورد عضویت اجباری
def force_join_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 عضویت در کانال", url="https://t.me/BloxyDesign")],
        [InlineKeyboardButton(text="✔️ تایید عضویت", callback_data="check_join")]
    ])


@router.message(CommandStart())
async def start(message: Message, bot: Bot):

    # ------------------------------
    # چک عضویت اجباری
    # ------------------------------
    try:
        member = await bot.get_chat_member(CHANNEL_ID, message.from_user.id)
        if member.status in ["left", "kicked"]:
            await message.answer(
                "⚠️ برای استفاده از ربات باید ابتدا در کانال عضو شوید:",
                reply_markup=force_join_keyboard()
            )
            return
    except:
        await message.answer(
            "⚠️ برای استفاده از ربات باید ابتدا در کانال عضو شوید:",
            reply_markup=force_join_keyboard()
        )
        return

    # ------------------------------
    # سیستم رفرال (نسخه بدون باگ)
    # ------------------------------
    args = message.text.split()

    async with AsyncSessionLocal() as session:

        # چک کن کاربر قبلاً ثبت شده یا نه
        result = await session.execute(
            select(User).where(User.id == message.from_user.id)
        )
        user = result.scalar_one_or_none()

        if not user:

            referred_by = None

            # اگر لینک رفرال وجود داشت
            if len(args) > 1:
                try:
                    referred_by = int(args[1])
                except:
                    referred_by = None

            # جلوگیری از اینکه کاربر خودش را رفرال کند
            if referred_by == message.from_user.id:
                referred_by = None

            # ساخت کاربر جدید
            new_user = User(
                id=message.from_user.id,
                username=message.from_user.username,
                referred_by=referred_by
            )
            session.add(new_user)

            # اگر رفرال معتبر بود → امتیاز بده
            if referred_by:
                ref_result = await session.execute(
                    select(User).where(User.id == referred_by)
                )
                ref_user = ref_result.scalar_one_or_none()

                if ref_user:
                    ref_user.referrals_count += 1

            await session.commit()

    # ------------------------------
    # پیام خوش‌آمد
    # ------------------------------

    photo = FSInputFile("designs.jpg")

    caption = (
        "🎉 *به دنیای طراحی‌های اختصاصی بلاکسی خوش آمدید\\!*\\n\\n"
        "اینجا جاییه که می‌تونی پروفایل‌های حرفه‌ای، تمیز و چشم‌نواز مخصوص خودت بسازی\\.\\n\\n"
        "برای شروع، فقط کافیه *لینک رفرال اختصاصی خودت* رو دریافت کنی و با دعوت دوستانت "
        "امتیاز لازم برای ثبت سفارش رو جمع کنی\\.\\n\\n"
        "📩 ارتباط با طراح:\\n"
        "\\@BloxyDesign"
    )

    await message.answer_photo(
        photo=photo,
        caption=caption,
        parse_mode="MarkdownV2"
    )

    await message.answer("👇 از منوی زیر استفاده کنید:", reply_markup=main_menu)


# ------------------------------
# هندلر دکمه «تایید عضویت»
# ------------------------------
@router.callback_query(lambda c: c.data == "check_join")
async def check_join(callback, bot: Bot):

    try:
        member = await bot.get_chat_member(CHANNEL_ID, callback.from_user.id)
        if member.status != "left":
            await callback.message.edit_text("✔️ عضویت تایید شد. دوباره /start بزنید.")
        else:
            await callback.answer("❌ هنوز عضو کانال نیستی!", show_alert=True)
    except:
        await callback.answer("❌ هنوز عضو کانال نیستی!", show_alert=True)
