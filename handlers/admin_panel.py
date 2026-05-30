# handlers/admin_panel.py
import os
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy import select

from database.models import AsyncSessionLocal, User

logger = logging.getLogger(__name__)
router = Router()

ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

# حالت‌های FSM برای پنل ادمین
class AdminStates(StatesGroup):
    waiting_for_user_id = State()
    waiting_for_amount = State()
    waiting_for_set_amount = State()


# کیبورد پنل ادمین
def admin_panel_keyboard():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ افزودن رفرال", callback_data="admin_add_ref")],
        [InlineKeyboardButton(text="✏️ تنظیم مستقیم رفرال", callback_data="admin_set_ref")],
        [InlineKeyboardButton(text="🔎 نمایش رفرال کاربر", callback_data="admin_view_ref")],
    ])
    return kb


# فرمان باز کردن پنل (فقط ادمین)
@router.message(F.text == "/admin")
async def open_admin_panel(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer("پنل ادمین باز شد. یکی از گزینه‌ها را انتخاب کن:", reply_markup=admin_panel_keyboard())


# هندلر کلیک روی دکمه‌ها
@router.callback_query()
async def admin_panel_callbacks(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("شما دسترسی ندارید.", show_alert=True)
        return

    data = callback.data or ""
    if data == "admin_add_ref":
        await callback.message.answer("شناسه کاربر را وارد کن (مثال: 123456789):")
        await state.set_state(AdminStates.waiting_for_user_id)
        await callback.answer()
        return

    if data == "admin_set_ref":
        await callback.message.answer("شناسه کاربر را وارد کن تا مقدار رفرال او را تنظیم کنم:")
        await state.set_state(AdminStates.waiting_for_user_id)
        # برای تشخیص مسیر بعدی، ذخیره کن که این بار قصد set داریم
        await state.update_data(mode="set")
        await callback.answer()
        return

    if data == "admin_view_ref":
        await callback.message.answer("شناسه کاربر را وارد کن تا رفرال او را نمایش دهم:")
        await state.set_state(AdminStates.waiting_for_user_id)
        await state.update_data(mode="view")
        await callback.answer()
        return

    # اگر callback نامشخص بود
    await callback.answer()


# دریافت شناسه کاربر (مرحله اول برای add/set/view)
@router.message(AdminStates.waiting_for_user_id)
async def admin_receive_user_id(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return

    text = message.text.strip()
    try:
        user_id = int(text)
    except ValueError:
        await message.answer("شناسه نامعتبر است. لطفاً فقط عدد وارد کن.")
        return

    data = await state.get_data()
    mode = data.get("mode", "add")  # پیش‌فرض افزودن

    # ذخیره شناسه و ادامه بر اساس حالت
    await state.update_data(target_user_id=user_id)

    if mode == "view":
        # نمایش مقدار فعلی رفرال
        async with AsyncSessionLocal() as session:
            user = await session.get(User, user_id)
            refs = user.referrals_count if user and user.referrals_count else 0
        await message.answer(f"🔎 کاربر {user_id} دارای {refs} رفرال است.")
        await state.clear()
        return

    if mode == "set":
        await message.answer("مقدار جدید رفرال را وارد کن (مثلاً 5):")
        await state.set_state(AdminStates.waiting_for_set_amount)
        return

    # حالت پیش‌فرض: افزودن رفرال (add)
    await message.answer("مقدار رفرال که می‌خواهی اضافه کنی را وارد کن (مثلاً 3):")
    await state.set_state(AdminStates.waiting_for_amount)


# دریافت مقدار برای افزودن رفرال
@router.message(AdminStates.waiting_for_amount)
async def admin_receive_amount(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return

    text = message.text.strip()
    try:
        amount = int(text)
    except ValueError:
        await message.answer("مقدار نامعتبر است. لطفاً یک عدد صحیح وارد کن.")
        return

    data = await state.get_data()
    user_id = data.get("target_user_id")
    if not user_id:
        await message.answer("شناسه کاربر پیدا نشد. دوباره از منو شروع کن (/admin).")
        await state.clear()
        return

    async with AsyncSessionLocal() as session:
        user = await session.get(User, user_id)
        if not user:
            # اگر کاربر در DB نیست، می‌توانیم یک رکورد جدید بسازیم یا خطا بدهیم.
            # اینجا خطا می‌دهیم تا از ایجاد رکورد ناخواسته جلوگیری شود.
            await message.answer(f"کاربر با شناسه {user_id} در دیتابیس پیدا نشد.")
            await state.clear()
            return

        current = user.referrals_count or 0
        user.referrals_count = current + amount
        await session.commit()

    await message.answer(f"✅ به کاربر {user_id} مقدار {amount} رفرال اضافه شد. (از {current} به {user.referrals_count})")
    await state.clear()


# دریافت مقدار برای تنظیم مستقیم رفرال
@router.message(AdminStates.waiting_for_set_amount)
async def admin_receive_set_amount(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return

    text = message.text.strip()
    try:
        new_value = int(text)
    except ValueError:
        await message.answer("مقدار نامعتبر است. لطفاً یک عدد صحیح وارد کن.")
        return

    data = await state.get_data()
    user_id = data.get("target_user_id")
    if not user_id:
        await message.answer("شناسه کاربر پیدا نشد. دوباره از منو شروع کن (/admin).")
        await state.clear()
        return

    async with AsyncSessionLocal() as session:
        user = await session.get(User, user_id)
        if not user:
            await message.answer(f"کاربر با شناسه {user_id} در دیتابیس پیدا نشد.")
            await state.clear()
            return

        old = user.referrals_count or 0
        user.referrals_count = max(0, new_value)
        await session.commit()

    await message.answer(f"✅ رفرال کاربر {user_id} از {old} به {user.referrals_count} تنظیم شد.")
    await state.clear()


# اختیاری: دستور سریع /giveref برای ادمین (همانند قبل)
@router.message(F.text.startswith("/giveref"))
async def give_ref_quick(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    parts = message.text.split()
    if len(parts) != 3:
        await message.reply("Usage: /giveref <user_id> <amount>")
        return

    try:
        user_id = int(parts[1])
        amount = int(parts[2])
    except ValueError:
        await message.reply("شناسه یا مقدار نامعتبر است.")
        return

    async with AsyncSessionLocal() as session:
        user = await session.get(User, user_id)
        if not user:
            await message.reply("کاربر پیدا نشد.")
            return
        current = user.referrals_count or 0
        user.referrals_count = current + amount
        await session.commit()
        await message.reply(f"رفرال‌های کاربر {user_id} از {current} به {user.referrals_count} افزایش یافت.")
