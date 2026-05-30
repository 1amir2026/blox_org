from aiogram import Router, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message, FSInputFile
from sqlalchemy import select
import re
import logging

from keyboards.main import main_menu
from database.models import AsyncSessionLocal, User
from handlers.membership import check_membership, force_join_keyboard

router = Router()
logging.basicConfig(level=logging.INFO)

CHANNEL_ID = -1002100624495

# تابع کمکی برای escape کردن متن در MarkdownV2
# از رشتهٔ معمولی با بک‌اسلش‌های escape شده استفاده شده تا SyntaxError پیش نیاد
MDV2_SPECIAL = '[_*\

\[\\]

()~`>#+\\-=|{}\\.!]'

def escape_md_v2(text: str) -> str:
    return re.sub(MDV2_SPECIAL, lambda m: "\\" + m.group(0), text)


@router.message(CommandStart())
async def start(message: Message, bot: Bot):
    logging.info("start handler hit for user %s", message.from_user.id)

    # حذف webhook در صورت وجود تا از Conflict جلوگیری شود
    try:
        await bot.delete_webhook(drop_pending_updates=True)
    except Exception as e:
        logging.debug("delete_webhook failed or not needed: %s", e)

    # ============================
    # 1) ذخیره رفرال قبل از چک عضویت
    # ============================
    args = message.text.split()

    try:
        async with AsyncSessionLocal() as session:

            result = await session.execute(
                select(User).where(User.id == message.from_user.id)
            )
            user = result.scalar_one_or_none()

            if not user:
                referred_by = None

                if len(args) > 1:
                    try:
                        referred_by = int(args[1])
                    except:
                        referred_by = None

                if referred_by == message.from_user.id:
                    referred_by = None

                new_user = User(
                    id=message.from_user.id,
                    username=message.from_user.username,
                    referred_by=referred_by
                )
                session.add(new_user)

                if referred_by:
                    ref_result = await session.execute(
                        select(User).where(User.id == referred_by)
                    )
                    ref_user = ref_result.scalar_one_or_none()

                    if ref_user:
                        ref_user.referrals_count += 1

                await session.commit()

    except Exception as e:
        logging.exception("Database error in start handler: %s", e)
        # ادامه می‌دهیم تا کاربر پیام خوش‌آمد را ببیند حتی اگر DB خطا داده باشد

    # ============================
    # 2) چک عضویت بعد از ذخیره رفرال
    # ============================
    try:
        if not await check_membership(bot, message.from_user.id):
            await message.answer(
                "⚠️ برای استفاده از ربات باید ابتدا در کانال عضو شوید:",
                reply_markup=force_join_keyboard()
            )
            return
    except Exception as e:
        logging.exception("check_membership error: %s", e)
        await message.answer("❗ خطا در بررسی عضویت. لطفا دوباره تلاش کن.")
        return

    # ============================
    # 3) پیام خوش‌آمد (با escape برای MarkdownV2)
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

    safe_caption = escape_md_v2(caption)

    try:
        await message.answer_photo(
            photo=photo,
            caption=safe_caption,
            parse_mode="MarkdownV2"
        )
    except Exception as e:
        logging.exception("Failed to send welcome photo with MarkdownV2: %s", e)
        # fallback: ارسال بدون فرمت
        try:
            await message.answer_photo(photo=photo, caption=caption, parse_mode=None)
        except Exception as e2:
            logging.exception("Fallback send failed: %s", e2)

    # منوی اصلی
    try:
        await message.answer("👇 از منوی زیر استفاده کنید:", reply_markup=main_menu)
    except Exception as e:
        logging.exception("Failed to send main menu: %s", e)


@router.callback_query(lambda c: c.data == "check_join")
async def check_join(callback, bot: Bot):
    try:
        if await check_membership(bot, callback.from_user.id):
            await callback.message.edit_text("✔️ عضویت تایید شد. دوباره /start بزنید.")
        else:
            await callback.answer("❌ هنوز عضو کانال نیستی!", show_alert=True)
    except Exception as e:
        logging.exception("check_join error: %s", e)
        await callback.answer("❗ خطا در بررسی عضویت. بعدا تلاش کن.", show_alert=True)
