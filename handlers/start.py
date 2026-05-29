from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton

from sqlalchemy import select

from keyboards.main import main_menu
from database.models import AsyncSessionLocal, User

router = Router()


@router.message(CommandStart())
async def start(message: Message):

    args = message.text.split()

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
                    pass

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

    # ------------------------------
    # کیبورد دکمه عضویت در کانال
    # ------------------------------

    join_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📢 عضویت در کانال", url="https://t.me/BloxyDesign")]
        ]
    )

    # ------------------------------
    # ارسال عکس + متن خوش‌آمد
    # ------------------------------

    photo = FSInputFile("designs.jpg")

    caption = (
        "🎉 *به دنیای طراحی‌های اختصاصی بلاکسی خوش آمدید!*\\n\\n"
        "اینجا جاییه که می‌تونی پروفایل‌های حرفه‌ای، تمیز و چشم‌نواز مخصوص خودت بسازی؛ "
        "پروفایل‌هایی که دقیقاً مطابق سلیقه‌ت طراحی می‌شن و ظاهر اکانتت رو چند برابر جذاب‌تر می‌کنن\\.\\n\\n"
        "برای شروع، فقط کافیه *لینک رفرال اختصاصی خودت* رو دریافت کنی و با دعوت دوستانت، "
        "امتیاز لازم برای ثبت سفارش رو جمع کنی\\. هر کاربری که با لینک تو وارد بات بشه، "
        "یک قدم به دریافت پروفایل حرفه‌ای نزدیک‌تر می‌شی\\.\\n\\n"
        "این بات کاملاً ساده، سریع و بدون پیچیدگی طراحی شده تا تجربه‌ای راحت و روان داشته باشی\\. "
        "تمام مراحل — از دریافت لینک رفرال تا انتخاب طرح و ارسال اسکین — مرحله‌به‌مرحله و بدون دردسر انجام می‌شه\\.\\n\\n"
        "اگر آماده‌ای، همین حالا شروع کن و اولین قدم رو بردار\\.\\n\\n"
        "📩 ارتباط با طراح:\\n"
        "@BloxyDesign"
    )

    await message.answer_photo(
        photo=photo,
        caption=caption,
        reply_markup=join_keyboard,
        parse_mode="MarkdownV2"
    )

    # بعد از عکس، کیبورد اصلی هم بیاد
    await message.answer("👇 از منوی زیر استفاده کنید:", reply_markup=main_menu)
