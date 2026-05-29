from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from sqlalchemy import select

from database.models import AsyncSessionLocal, User

router = Router()


# ====================== کیبورد طرح‌ها ======================
def design_inline_keyboard():
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="طرح ۱", callback_data="design_1")],
        [InlineKeyboardButton(text="طرح ۲", callback_data="design_2")],
        [InlineKeyboardButton(text="طرح ۳", callback_data="design_3")]
    ])


# ====================== درخواست پروفایل ======================
@router.message(F.text == "🖼 درخواست پروفایل")
async def request_profile(message: Message, state: FSMContext):
    async with AsyncSessionLocal() as session:
        user = await session.get(User, message.from_user.id)
        
        if not user or user.referrals_count < REFERRAL_NEEDED:
            await message.answer(
                f"❌ شما هنوز شرط لازم را ندارید.\n"
                f"تعداد رفرال شما: {user.referrals_count if user else 0}/5"
            )
            return

    # ارسال عکس طرح‌ها + دکمه‌ها
    photo = FSInputFile("designs.jpg")   # اسم فایل باید دقیقاً designs.jpg باشد

    await message.answer_photo(
        photo=photo,
        caption="🎨 لطفاً طرح مورد نظر خود را انتخاب کنید:",
        reply_markup=design_inline_keyboard()
    )
    
    await state.set_state(ProfileStates.choosing_design)


# ====================== انتخاب طرح ======================
@router.callback_query(F.data.startswith("design_"))
async def choose_design(callback: CallbackQuery, state: FSMContext):
    design_num = callback.data.split("_")[1]
    await state.update_data(design=design_num)
    
    await callback.message.edit_caption(
        caption="💡 حالا رنگ نورپردازی را انتخاب کنید:",
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
    light_color = callback.data.split("_")[1]
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
    bg_color = callback.data.split("_")[1]
    await state.update_data(bg_color=bg_color)
    
    await callback.message.edit_caption(
        caption="✅ حالا اسکین خود را به صورت فایل PNG ارسال کنید."
    )
    await state.set_state(ProfileStates.waiting_for_skin)


# ====================== دریافت اسکین ======================
@router.message(ProfileStates.waiting_for_skin, F.document | F.photo)
async def receive_skin(message: Message, state: FSMContext):
    data = await state.get_data()
    
    caption = f"""
🆕 سفارش جدید پروفایل بلاکسی

👤 کاربر: {message.from_user.id}
📛 یوزرنیم: @{message.from_user.username or "ندارد"}
🎨 طرح: {data.get('design')}
💡 نور: {data.get('light_color')}
🖼 بکگراند: {data.get('bg_color')}
    """

    if message.photo:
        await message.bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=caption)
    else:
        await message.bot.send_document(ADMIN_ID, message.document.file_id, caption=caption)

    await message.answer("✅ سفارش شما با موفقیت به ادمین ارسال شد.\nبه زودی پروفایل برایتان ساخته و ارسال می‌شود.")
    await state.clear()