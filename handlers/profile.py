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
from handlers.membership import check_membership, force_join_keyboard   # ← فقط این اضافه شد

logger = logging.getLogger(__name__)
router = Router()

ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

REF_REQUIREMENTS = {
    "design_1": 2,
    "design_2": 3,
    "design_3": 5,
}

DESIGN_NAMES = {
    "design_1": "پروفایل 1",
    "design_2": "پروفایل 2",
    "design_3": "والپیپر",
}


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

    # 🔥 چک عضویت
    if not await check_membership(message.bot, message.from_user.id):
        await message.answer("⚠️ برای استفاده از این بخش باید عضو کانال باشید:", reply_markup=force_join_keyboard())
        return

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

    # 🔥 چک عضویت
    if not await check_membership(callback.bot, callback.from_user.id):
        await callback.message.answer("⚠️ برای ادامه باید عضو کانال باشید:", reply_markup=force_join_keyboard())
        return

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

        # 🎨 رنگ‌های جدید:
        [InlineKeyboardButton(text="🟢 سبز", callback_data="light_green")],
        [InlineKeyboardButton(text="🟡 زرد", callback_data="light_yellow")],
        [InlineKeyboardButton(text="🟠 نارنجی", callback_data="light_orange")],
        [InlineKeyboardButton(text="🌸 صورتی", callback_data="light_pink")],
        [InlineKeyboardButton(text="🟤 قهوه‌ای", callback_data="light_brown")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)



# ====================== انتخاب رنگ نور ======================
@router.callback_query(F.data.startswith("light_"))
async def choose_light(callback: CallbackQuery, state: FSMContext):

    # 🔥 چک عضویت
    if not await check_membership(callback.bot, callback.from_user.id):
        await callback.message.answer("⚠️ برای ادامه باید عضو کانال باشید:", reply_markup=force_join_keyboard())
        return

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
        [InlineKeyboardButton(text="🔴 قرمز", callback_data="light_red")],
        [InlineKeyboardButton(text="⚪ سفید", callback_data="light_white")],

        # 🎨 رنگ‌های جدید:
        [InlineKeyboardButton(text="🟢 سبز", callback_data="bg_green")],
        [InlineKeyboardButton(text="🟡 زرد", callback_data="bg_yellow")],
        [InlineKeyboardButton(text="🟠 نارنجی", callback_data="bg_orange")],
        [InlineKeyboardButton(text="🌸 صورتی", callback_data="bg_pink")],
        [InlineKeyboardButton(text="🟤 قهوه‌ای", callback_data="bg_brown")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


# ====================== انتخاب رنگ بکگراند ======================
@router.callback_query(F.data.startswith("bg_"))
async def choose_bg(callback: CallbackQuery, state: FSMContext):

    # 🔥 چک عضویت
    if not await check_membership(callback.bot, callback.from_user.id):
        await callback.message.answer("⚠️ برای ادامه باید عضو کانال باشید:", reply_markup=force_join_keyboard())
        return

    bg_color = callback.data.split("_", 1)[1]
    await state.update_data(bg_color=bg_color)

    try:
        await callback.message.edit_caption(
            caption="✅ حالا فقط فایل اسکین را به‌صورت فایل (Send as File) ارسال کنید."
        )
    except Exception:
        await callback.message.answer("✅ حالا فقط فایل اسکین را به‌صورت فایل (Send as File) ارسال کنید.")

    await state.set_state(ProfileStates.waiting_for_skin)


# ====================== دریافت اسکین ======================
@router.message(ProfileStates.waiting_for_skin)
async def receive_skin_only_file_image(message: Message, state: FSMContext):

    # 🔥 چک عضویت
    if not await check_membership(message.bot, message.from_user.id):
        await message.answer("⚠️ برای ادامه باید عضو کانال باشید:", reply_markup=force_join_keyboard())
        return

    if not message.document:
        await message.answer("❗ لطفاً عکس را به‌صورت *فایل* ارسال کن (Send as File). عکس‌های معمولی پذیرفته نمی‌شوند.")
        return

    mime = getattr(message.document, "mime_type", "") or ""
    if not mime.startswith("image/"):
        await message.answer("❗ فایل ارسال‌شده تصویر نیست. لطفاً همان تصویر را به‌صورت فایل ارسال کن.")
        return

    data = await state.get_data()
    design_action = data.get("design")

    if not design_action:
        await message.answer("❗ خطا: طرح انتخابی پیدا نشد.")
        await state.clear()
        return

    required = REF_REQUIREMENTS.get(design_action, 1)
    design_name = DESIGN_NAMES.get(design_action, "سفارش")

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
                f"لینک رفرال شما:\n{ref_link}"
            )
            await state.clear()
            return

    caption = (
        "🆕 سفارش جدید پروفایل بلاکسی\n\n"
        f"👤 کاربر: {message.from_user.id}\n"
        f"📛 یوزرنیم: @{message.from_user.username or 'ندارد'}\n"
        f"🎨 طرح: {design_name}\n"
        f"💡 نور: {data.get('light_color')}\n"
        f"🖼 بکگراند: {data.get('bg_color')}\n"
    )

    try:
        await message.bot.send_document(
            ADMIN_ID,
            message.document.file_id,
            caption=caption
        )

        async with AsyncSessionLocal() as session:
            user = await session.get(User, message.from_user.id)
            if user and user.referrals_count >= required:
                user.referrals_count -= required
                await session.commit()

    except Exception as e:
        logger.exception("Failed to send order to admin: %s", e)
        await message.answer("❗ خطا در ارسال سفارش به ادمین.")
        await state.clear()
        return

    await message.answer("✅ سفارش شما ارسال شد. به زودی پروفایل آماده می‌شود.")
    await state.clear()
