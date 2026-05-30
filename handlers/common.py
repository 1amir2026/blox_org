# handlers/common.py  (ادامه)
import os
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

@router.message(F.text == "👨🏻‍💻 پنل ادمین")
async def open_admin_panel_via_reply_button(message: Message):
    # دوباره چک کن که فقط ادمین وارد شود
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ شما دسترسی به پنل ادمین ندارید.")
        return

    # نمایش منوی پنل ادمین با دکمه‌های عملیاتی (می‌تونی callbackها را به handlers/admin_panel وصل کنی)
    await message.answer(
        "🔐 پنل ادمین:\n"
        "➕ افزودن رفرال\n"
        "✏️ تنظیم رفرال\n"
        "🔎 نمایش رفرال کاربر\n\n"
        "برای استفاده از هر گزینه، روی متن مربوطه کلیک کن یا از دکمه‌های بعدی استفاده کن."
    )
