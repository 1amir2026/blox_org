# handlers/profile.py
import os
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext

from sqlalchemy import select

from database.models import AsyncSessionLocal, User
from utils.states import ProfileStates

router = Router()

ADMIN_ID = int(os.getenv("ADMIN_ID"))
# دیگر از REFERRAL_NEEDED کلی استفاده نمی‌کنیم؛ نیاز هر طرح جداگانه تعریف می‌شود
# REFERRAL_NEEDED = int(os.getenv("REFERRAL_NEEDED", 1))

# نیازمندی رفرال برای هر طرح (بر اساس callback_data)
REF_REQUIREMENTS = {
    "design_1": 2,   # پروفایل 1 نیاز به 2 رفرال دارد
    "design_2": 3,   # پروفایل 2 نیاز به 3 رفرال دارد
    "design_3": 5,   # والپیپر نیاز به 5 رفرال دارد
}

# نام خوان برای نمایش در پیام‌ها
DESIGN_NAMES = {
    "design_1": "پروفایل 1",
    "design_2": "پروفایل 2",
    "design_3": "والپیپر",
}


# ====================== کیبورد طرح‌ها ======================
def design_inline_keyboard():
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="پروفایل 1", callback_data="design_1")],
        [InlineKeyboardButton(text="پروفایل 2", callback_data="design_2")],
        [InlineKeyboardButton(text="والپیپر", callback_data="design_3")]
    ])


# ====================== درخواست پروفایل ======================
@router.message(F.text == "🖼 درخواست پروفایل")
async def request_profile(message: Message, state: FSMContext):

    # وارد مرحله انتخاب طرح می‌شه (رفرال در مرحله ارسال اسکین چک می‌شود)
    photo = FSInputFile("designs.jpg")

    await message.answer_photo(
        photo=photo,
        caption="🎨 لطفاً طرح مورد نظر خود را انتخاب کنید:",
        reply_markup=design_inline_keyboard()
    )

    await state.set_state(ProfileStates.choosing_design)


# ====================== انتخاب طرح ======================
@router.callback_query(F.data.startswith("design_"))
async def choose_design(callback: CallbackQuery, state: FSMContext):
    # ذخیرهٔ callback کامل (مثلاً "design_1")
    action = callback.data
    await state.update_data(design=action)

    # نمایش مرحله بعد (انتخاب نور) — نام طرح را هم می‌توان نمایش داد
    name = DESIGN_NAMES.get(action, "طرح انتخابی")
    await callback.message.edit_caption(
        caption=f"💡 شما {name} را انتخاب کردید.\n\nحال رنگ نورپردازی را انتخاب کنید:",
        reply_markup=light_color_keyboard()
    )

    await state.set_state(ProfileStates.choosing_light_color)


def light_color_keyboard():
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔴 قرمز", callback_data="light_red")],
        [InlineKeyboardButton(text="🔵 آبی", callback_data="light_blue")],
        [InlineKeyboardButton(text="🟣 بنفش", callback_data="light_purple")],
        [InlineKeyboardButton(text="⚪ سفید", callback_data="light_white")]
    ])


# ====================== انتخاب رنگ نور ======================
@router.callback_query(F.data.startswith("light_"))
async def choose_light(callback: CallbackQuery, state: FSMContext):
    light_color = callback.data.split("_", 1)[1]
    await state.update_data(light_color=light_color)

    await callback.message.edit_caption(
        caption="🖼 حالا رنگ پس‌زمینه را انتخاب کنید:",
        reply_markup=bg_color_keyboard()
    )

    await state.set_state(ProfileStates.choosing_bg_color)


def bg_color_keyboard():
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬛ مشکی", callback_data="bg_black")],
        [InlineKeyboardButton(text="🌊 آبی تیره", callback_data="bg_darkblue")],
        [InlineKeyboardButton(text="🟣 بنفش", callback_data="bg_purple")]
    ])


# ====================== انتخاب رنگ بکگراند ======================
@router.callback_query(F.data.startswith("bg_"))
async def choose_bg(callback: CallbackQuery, state: FSMContext):
    bg_color = callback.data.split("_", 1)[1]
    await state.update_data(bg_color=bg_color)

    await callback.message.edit_caption(
        caption="✅ حالا *فقط فایل اسکین* را ارسال کنید.",
        parse_mode="Markdown"
    )

    await state.set_state(ProfileStates.waiting_for_skin)


# ====================== دریافت اسکین ======================
@router.message(ProfileStates.waiting_for_skin)
async def receive_skin(message: Message, state: FSMContext):

    # فقط فایل قبول می‌کنیم
    if not message.document:
        await message.answer("❗ لطفاً فقط *فایل اسکین* ارسال کنید.", parse_mode="Markdown")
        return

    data = await state.get_data()
    design_action = data.get("design")  # مثلاً "design_1"
    if not design_action:
        # اگر به هر دلیلی طرح ذخیره نشده بود، کاربر را به منو برگردان
        await message.answer("❗ خطا: طرح انتخابی پیدا نشد. دوباره از منو انتخاب کنید.")
        await state.clear()
        return

    # مقدار مورد نیاز برای طرح انتخابی
    required = REF_REQUIREMENTS.get(design_action, 1)
    design_name = DESIGN_NAMES.get(design_action, "سفارش")

    # چک رفرال بر اساس طرح انتخابی
    async with AsyncSessionLocal() as session:
        user = await session.get(User, message.from_user.id)

        current_refs = user.referrals_count if user and user.referrals_count else 0

        if current_refs < required:
            need = required - current_refs
            # ساخت لینک رفرال
            me = await message.bot.get_me()
            ref_link = f"https://t.me/{me.username}?start={message.from_user.id}"

            await message.answer(
                f"⚠️ برای سفارش *{design_name}* نیاز به *{required}* رفرال داری.\n"
                f"🔹 شما اکنون: *{current_refs}* رفرال داری.\n"
                f"🔸 برای تکمیل نیاز، *{need}* رفرال دیگر لازم است.\n\n"
                f"لینک رفرال شما:\n{ref_link}\n\n"
                "دوستات رو دعوت کن و بعد دوباره تلاش کن.",
                parse_mode="Markdown"
            )
            await state.clear()
            return

        # اگر رفرال کافی بود → ارسال سفارش به ادمین (یا ثبت در DB)
        caption = f"""
🆕 سفارش جدید پروفایل بلاکسی

👤 کاربر: {message.from_user.id}
📛 یوزرنیم: @{message.from_user.username or "ندارد"}
🎨 طرح: {design_name}
💡 نور: {data.get('light_color')}
🖼 بکگراند: {data.get('bg_color')}
        """

        # ارسال فایل به ادمین
        await message.bot.send_document(
            ADMIN_ID,
            message.document.file_id,
            caption=caption
        )

        # (اختیاری) اگر می‌خواهی رفرال‌ها پس از ثبت سفارش کسر شوند، اینجا انجام بده:
        # user.referrals_count = current_refs - required
        # await session.commit()

        await message.answer("✅ سفارش شما ارسال شد. به زودی پروفایل برایتان ساخته می‌شود.")
        await state.clear()
