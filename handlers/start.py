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

# کانال (در صورت نیاز استفاده کن)
CHANNEL_ID = -1002100624495

# تابع کمکی برای escape کردن متن در MarkdownV2
MDV2_SPECIAL = r'[_*

\[\]

()~`>#+\-=|{}.!]'

def escape_md_v2(text: str) -> str:
    return re.sub(MDV2_SPECIAL, lambda m: "\\" + m.group(0), text)


@router.message(CommandStart())
async def start(message: Message, bot: Bot):
    """
    هندلر /start:
    - رفرال را قبل از چک عضویت ذخیره می‌کند
    - در صورت وجود webhook فعال، آن را حذف می‌کند تا Conflict رفع شود
    - متن خوش‌آمد با escape مناسب ارسال می‌شود
    - لاگ‌گذاری برای دیباگ اضافه شده
    """

    logging.info("start handler hit for user %s", message.from_user.id)

    # حذف webhook (اگر webhook ست شده باشد) تا Conflict با polling رفع شود
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
        # اگر چک عضویت خطا داد، اجازه بده کاربر ادامه دهد یا پیام خطا بده
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
            parse_mode=None
        )
    except Exception as e:
        logging.exception("Failed to send welcome photo with MarkdownV2: %s", e)
        # اگر MarkdownV2 مشکل داشت، متن ساده بفرست
        try:
            await message.answer_photo(photo=photo, caption=caption, parse_mode=None)
        except Exception as e2:
            logging.exception("Fallback send failed: %s", e2)

    # منوی اصلی
    try:
        await message.answer("👇 از منوی زیر استفاده کنید:", reply_markup=main_menu)
    except Exception as e:
        logging.exception("Failed to send main menu: %s", e)


# ============================
# دکمه تایید عضویت
# ============================
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
