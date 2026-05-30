from aiogram import Router, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message, FSInputFile
from sqlalchemy import select

from keyboards.main import main_menu
from database.models import AsyncSessionLocal, User
from handlers.membership import check_membership, force_join_keyboard

router = Router()

CHANNEL_ID = -1002100624495


@router.message(CommandStart())
async def start(message: Message, bot: Bot):

    # ============================
    # 1) ذخیره رفرال قبل از چک عضویت
    # ============================

    args = message.text.split()

    async with AsyncSessionLocal() as session:

        result = await session.execute(
            select(User).where(User.id == message.from_user.id)
        )
        user = result.scalar_one_or_none()

        # اگر کاربر جدید است → رفرال ثبت شود
        if not user:

            referred_by = None

            # اگر لینک رفرال وجود داشت
            if len(args) > 1:
                try:
                    referred_by = int(args[1])
                except:
                    referred_by = None

            # جلوگیری از رفرال خودکار
            if referred_by == message.from_user.id:
                referred_by = None

            # ثبت کاربر جدید
            new_user = User(
                id=message.from_user.id,
                username=message.from_user.username,
                referred_by=referred_by
            )
            session.add(new_user)

            # افزایش رفرال معرف
            if referred_by:
                ref_result = await session.execute(
                    select(User).where(User.id == referred_by)
                )
                ref_user = ref_result.scalar_one_or_none()

                if ref_user:
                    ref_user.referrals_count += 1

            await session.commit()

    # ============================
    # 2) چک عضویت بعد از ذخیره رفرال
    # ============================

    if not await check_membership(bot, message.from_user.id):
        await message.answer(
            "⚠️ برای استفاده از ربات باید ابتدا در کانال عضو شوید:",
            reply_markup=force_join_keyboard()
        )
        return

    # ============================
    # 3) پیام خوش‌آمد
    # ============================

    photo = FSInputFile("designs.jpg")

    caption = (
        "🎉 *به دنیای طراحی‌های اختصاصی بلاکسی خوش آمدید!*"
        "\n\n"
        "اینجا جاییه که می‌تونی پروفایل‌های حرفه‌ای، تمیز و چشم‌نواز مخصوص خودت بسازی."
        "\n\n"
        "برای شروع، فقط کافیه *لینک رفرال اختصاصی خودت* رو دریافت کنی و با دعوت دوستانت "
        "امتیاز لازم برای ثبت سفارش رو جمع کنی."
        "\n\n"
        "📩 ارتباط با طراح:\n"
        "@BloxyDesign"
    )

    await message.answer_photo(
        photo=photo,
        caption=caption,
        parse_mode="MarkdownV2"
    )

    await message.answer("👇 از منوی زیر استفاده کنید:", reply_markup=main_menu)


# ============================
# دکمه تایید عضویت
# ============================

@router.callback_query(lambda c: c.data == "check_join")
async def check_join(callback, bot: Bot):

    if await check_membership(bot, callback.from_user.id):
        await callback.message.edit_text("✔️ عضویت تایید شد. دوباره /start بزنید.")
    else:
        await callback.answer("❌ هنوز عضو کانال نیستی!", show_alert=True)
