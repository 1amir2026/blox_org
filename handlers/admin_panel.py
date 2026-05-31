# handlers/admin_panel.py
import os
from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy import select

from database.models import AsyncSessionLocal, User

router = Router()

ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

# ------------------ حالت‌ها ------------------
class AdminStates(StatesGroup):
    waiting_user_id = State()
    waiting_amount = State()
    waiting_set_amount = State()
    waiting_broadcast = State()   # ← اضافه شد


# ------------------ کیبورد پنل ادمین ------------------
def admin_panel_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ افزودن رفرال", callback_data="admin_add")],
        [InlineKeyboardButton(text="✏️ تنظیم رفرال", callback_data="admin_set")],
        [InlineKeyboardButton(text="🔎 نمایش رفرال", callback_data="admin_view")],
        [InlineKeyboardButton(text="📢 اطلاع‌رسانی", callback_data="admin_broadcast")],  # ← اضافه شد
        [InlineKeyboardButton(text="🔙 بازگشت", callback_data="admin_back")],
    ])


# ------------------ ورود به پنل ------------------
@router.message(F.text.contains("پنل ادمین"))
async def admin_panel(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ شما ادمین نیستید.")
        return

    await message.answer("🔐 پنل ادمین:", reply_markup=admin_panel_keyboard())


# ------------------ هندلر دکمه‌ها ------------------
@router.callback_query(F.data.startswith("admin_"))
async def admin_actions(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ دسترسی ندارید.", show_alert=True)
        return

    action = callback.data
    await callback.answer()

    if action in ("admin_add", "admin_set", "admin_view"):
        await callback.message.answer("🔢 شناسه کاربر را بفرست:")
        await state.set_state(AdminStates.waiting_user_id)
        await state.update_data(mode=action)
        return

    # 🔥 اطلاع‌رسانی
    if action == "admin_broadcast":
        await callback.message.answer("📝 پیام خود را ارسال کنید تا برای همه کاربران فرستاده شود:")
        await state.set_state(AdminStates.waiting_broadcast)
        return

    if action == "admin_back":
        await callback.message.answer("🔙 به منوی اصلی برگشتی.")
        await state.clear()
        return


# ------------------ دریافت user_id ------------------
@router.message(AdminStates.waiting_user_id)
async def get_user_id(message: Message, state: FSMContext):
    raw = message.text or message.caption or ""

    try:
        user_id = int(raw)
    except:
        await message.answer("❗ شناسه نامعتبر است. فقط عدد بفرست.")
        return

    await state.update_data(target=user_id)
    data = await state.get_data()
    mode = data.get("mode")

    if mode == "admin_view":
        async with AsyncSessionLocal() as session:
            user = await session.get(User, user_id)
            refs = user.referrals_count if user else 0

        await message.answer(f"🔎 رفرال کاربر {user_id}: {refs}")
        await state.clear()
        return

    if mode == "admin_add":
        await message.answer("➕ چند رفرال اضافه کنم؟")
        await state.set_state(AdminStates.waiting_amount)
        return

    if mode == "admin_set":
        await message.answer("✏️ مقدار جدید رفرال را بفرست:")
        await state.set_state(AdminStates.waiting_set_amount)
        return


# ------------------ افزودن رفرال ------------------
@router.message(AdminStates.waiting_amount)
async def add_refs(message: Message, state: FSMContext):
    raw = message.text or message.caption or ""

    try:
        amount = int(raw)
    except:
        await message.answer("❗ مقدار نامعتبر است. فقط عدد بفرست.")
        return

    data = await state.get_data()
    user_id = data.get("target")

    async with AsyncSessionLocal() as session:
        user = await session.get(User, user_id)

        if not user:
            await message.answer("❗ کاربر پیدا نشد.")
            await state.clear()
            return

        old = user.referrals_count or 0
        user.referrals_count = old + amount
        await session.commit()

    await message.answer(f"✅ رفرال کاربر {user_id} از {old} → {user.referrals_count} افزایش یافت.")
    await state.clear()


# ------------------ تنظیم مستقیم رفرال ------------------
@router.message(AdminStates.waiting_set_amount)
async def set_refs(message: Message, state: FSMContext):
    raw = message.text or message.caption or ""

    try:
        amount = int(raw)
    except:
        await message.answer("❗ مقدار نامعتبر است. فقط عدد بفرست.")
        return

    data = await state.get_data()
    user_id = data.get("target")

    async with AsyncSessionLocal() as session:
        user = await session.get(User, user_id)

        if not user:
            await message.answer("❗ کاربر پیدا نشد.")
            await state.clear()
            return

        old = user.referrals_count or 0
        user.referrals_count = amount
        await session.commit()

    await message.answer(f"✏️ رفرال کاربر {user_id} از {old} → {amount} تنظیم شد.")
    await state.clear()


# ------------------ اطلاع‌رسانی به همه کاربران ------------------
@router.message(AdminStates.waiting_broadcast)
async def broadcast_message(message: Message, state: FSMContext):
    raw_msg = message

    await message.answer("⏳ در حال ارسال پیام به همه کاربران...")

    sent = 0
    failed = 0

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User.id))
        users = result.scalars().all()

    for user_id in users:
        try:
            # ارسال انواع پیام
            if raw_msg.text:
                await message.bot.send_message(user_id, raw_msg.text)

            elif raw_msg.photo:
                await message.bot.send_photo(user_id, raw_msg.photo[-1].file_id, caption=raw_msg.caption or "")

            elif raw_msg.video:
                await message.bot.send_video(user_id, raw_msg.video.file_id, caption=raw_msg.caption or "")

            elif raw_msg.document:
                await message.bot.send_document(user_id, raw_msg.document.file_id, caption=raw_msg.caption or "")

            else:
                await message.bot.forward_message(user_id, message.chat.id, raw_msg.message_id)

            sent += 1

        except:
            failed += 1
            continue

    await message.answer(f"✅ ارسال شد.\n\n📨 موفق: {sent}\n❌ ناموفق: {failed}")
    await state.clear()
