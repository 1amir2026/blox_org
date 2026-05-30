# handlers/profile.py
import os
import logging
from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
    FSInputFile,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.fsm.context import FSMContext
from sqlalchemy import select

from database.models import AsyncSessionLocal, User
from utils.states import ProfileStates

logger = logging.getLogger(__name__)
router = Router()

ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

# نیازمندی رفرال برای هر طرح
REF_REQUIREMENTS = {
    "design_1": 2,   # پروفایل 1 → 2 رفرال
    "design_2": 3,   # پروفایل 2 → 3 رفرال
    "design_3": 5,   # والپیپر → 5 رفرال
}

# نام طرح‌ها
DESIGN_NAMES = {
    "design_1": "پروفایل 1",
    "design_2": "پروفایل 2",
    "design_3": "والپیپر",
}


# ====================== کیبورد انتخاب طرح + کپشن ======================
async def design_keyboard_for_user_and_caption(user_id: int):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        current_refs = user.referrals_count if user and user.referrals_count else 0

    inline_keyboard = []
    for action in ["design_1", "design_2", "design_3"]:
        need = REF_REQUIREMENTS.get(action, 0)
        name = DESIGN_NAMES.get(action, action)
        btn = InlineKeyboardButton(text=f"{name} — نیاز: {need}", callback_data=action)
        inline_keyboard.append([btn])

    kb = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

    caption_lines = [
        "🎨 لطفاً طرح مورد نظر خود را انتخاب کنید",
        "",
        "🔹 نیازمندی رفرال برای هر طرح:",
    ]
    for action in ["design_1", "design_2", "design_3"]:
        need = REF_REQUIREMENTS.get(action, 0)
        name = DESIGN_NAMES.get(action, action)
        caption_lines.append(f"• {name} — نیاز: {need} رفرال")

    caption_lines.append("")
    caption_lines.append(f"🔸 رفرال فعلی شما: {current_refs}")
    caption = "\n".join(caption_lines)

    return kb, caption


# ====================== درخواست پروفایل ======================
@router.message(F.text == "🖼 درخواست پروفایل")
async def request_profile(message: Message, state: FSMContext):
    try:
        photo = FSInputFile("designs.jpg")
    except Exception:
        photo = None

    kb, caption = await design_keyboard_for_user_and_caption(message.from_user.id)

    if photo:
        await message.answer_photo(photo=photo, caption=caption, reply_markup=kb)
    else:
        await message.answer(caption, reply_markup=kb)

    await state.set_state(ProfileStates.choosing_design)


# ====================== انتخاب طرح ======================
@router.callback_query(F.data.startswith("design_"))
async def choose_design(callback: CallbackQuery, state: FSMContext):
    action = callback.data
    await state.update_data(design=action)

    name = DESIGN_NAMES.get(action, "طرح انتخابی")

    async with AsyncSessionLocal() as session:
        user = await session.get(User, callback.from_user.id)
        current_refs = user.referrals_count if user and user.referrals_count else 0

    required = REF_REQUIREMENTS.get(action, 0)

    await callback.message.answer(
        f"🔔 شما {current_refs} رفرال دارید. برای سفارش {name} نیاز به {required} رفرال است."
    )

    try:
        await callback.message.edit_caption(
            caption=f"💡 شما {name} را انتخاب کردید.\n\nحال رنگ نورپردازی را انتخاب کنید:",
            reply_markup=light_color_keyboard(),
        )
    except Exception:
        await callback.message.answer(
            f"💡 شما {name} را انتخاب کردید.\n\nحال رنگ نورپردازی را انتخاب کنید:",
            reply_markup=light_color_keyboard(),
        )

    await state.set_state(ProfileStates.choosing_light_color)


def light_color_keyboard():
    inline_keyboard = [
        [InlineKeyboardButton(text="🔴 قرمز", callback_data="light_red")],
        [InlineKeyboardButton(text="🔵 آبی", callback_data="light_blue")],
        [InlineKeyboardButton(text="🟣 بنفش", callback_data="light_purple")],
        [InlineKeyboardButton(text="⚪ سفید", callback_data="light_white")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


# ====================== انتخاب رنگ نور ======================
@router.callback_query(F.data.startswith("light_"))
async def choose_light(callback: CallbackQuery, state: FSMContext):
    light_color = callback.data.split("_", 1)[1]
    await state.update_data(light_color=light_color)

    try:
        await callback.message.edit_caption(
            caption="🖼 حالا رنگ پس‌زمینه را انتخاب کنید:",
            reply_markup=bg_color_keyboard()
        )
    except Exception:
        await callback.message.answer(
            "🖼 حالا رنگ پس‌زمینه را انتخاب کنید:",
            reply_markup=bg_color_keyboard()
        )

    await state.set_state(ProfileStates.choosing_bg_color)


def bg_color_keyboard():
    inline_keyboard = [
        [InlineKeyboardButton(text="⬛ مشکی", callback_data="bg_black")],
        [InlineKeyboardButton(text="🌊 آبی تیره", callback_data="bg_darkblue")],
        [InlineKeyboardButton(text="🟣 بنفش", callback_data="bg_purple")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


# ====================== انتخاب رنگ بکگراند ======================
@router.callback_query(F.data.startswith("bg_"))
async def choose_bg(callback: CallbackQuery, state: FSMContext):
    bg_color = callback.data.split("_", 1)[1]
    await state.update_data(bg_color=bg_color)

    try:
        await callback.message.edit_caption(
            caption="✅ حالا فقط فایل اسکین را به‌صورت فایل (Send as File) ارسال کنید."
        )
    except Exception:
        await callback.message.answer("✅ حالا فقط فایل اسکین را به‌صورت فایل (Send as File) ارسال کنید.")

    await state.set_state(ProfileStates.waiting_for_skin)


# ====================== دریافت اسکین (فقط document با mime image/*) ======================
@router.message(ProfileStates.waiting_for_skin)
async def receive_skin_only_file_image(message: Message, state: FSMContext):

    if not message.document:
        await message.answer("❗ لطفاً عکس را به‌صورت *فایل* ارسال کن (Send as File). عکس‌های معمولی (photo) پذیرفته نمی‌شوند.")
        return

    mime = getattr(message.document, "mime_type", "") or ""
    if not mime.startswith("image/"):
        await message.answer("❗ فایل ارسال‌شده تصویر نیست. لطفاً همان تصویر را به‌صورت فایل (image) ارسال کن.")
        return

    data = await state.get_data()
    design_action = data.get("design")

    if not design_action:
        await message.answer("❗ خطا: طرح انتخابی پیدا نشد. دوباره از منو انتخاب کنید.")
        await state.clear()
        return

    required = REF_REQUIREMENTS.get(design_action, 1)
    design_name = DESIGN_NAMES.get(design_action, "سفارش")

    # بررسی رفرال
    async with AsyncSessionLocal() as session:
        user = await session.get(User, message.from_user.id)
        current_refs = user.referrals_count if user and user.referrals_count else 0

        if current_refs < required:
            need = required - current_refs
            me = await message.bot.get_me()
            ref_link = f"https://t.me/{me.username}?start={message.from_user.id}"

            await message.answer(
                f"⚠️ برای سفارش {design_name} نیاز به {required} رفرال داری.\n"
                f"🔹 شما اکنون: {current_refs} رفرال داری.\n"
                f"🔸 برای تکمیل نیاز، {need} رفرال دیگر لازم است.\n\n"
                f"لینک رفرال شما:\n{ref_link}\n\n"
                "دوستات رو دعوت کن و بعد دوباره تلاش کن."
            )
            await state.clear()
            return

    # کپشن سفارش برای ادمین
    caption = (
        "🆕 سفارش جدید پروفایل بلاکسی\n\n"
        f"👤 کاربر: {message.from_user.id}\n"
        f"📛 یوزرنیم: @{message.from_user.username or 'ندارد'}\n"
        f"🎨 طرح: {design_name}\n"
        f"💡 نور: {data.get('light_color')}\n"
        f"🖼 بکگراند: {data.get('bg_color')}\n"
    )

    # ارسال سفارش به ادمین + کم کردن رفرال
    try:
        await message.bot.send_document(
            ADMIN_ID,
            message.document.file_id,
            caption=caption
        )

        # 🔥 کم کردن رفرال بر اساس طرح انتخابی
        async with AsyncSessionLocal() as session:
            user = await session.get(User, message.from_user.id)
            if user and user.referrals_count >= required:
                user.referrals_count -= required
                await session.commit()

    except Exception as e:
        logger.exception("Failed to send order to admin: %s", e)
        await message.answer("❗ خطا در ارسال سفارش به ادمین. لطفا بعدا تلاش کن.")
        await state.clear()
        return

    await message.answer("✅ سفارش شما ارسال شد. به زودی پروفایل برایتان ساخته می‌شود.")
    await state.clear()
