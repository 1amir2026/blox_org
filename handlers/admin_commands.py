import os
from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy import select

from database.models import AsyncSessionLocal, User

router = Router()

ADMIN_ID = int(os.getenv("ADMIN_ID"))


@router.message(F.text.startswith("/giveref"))
async def give_ref(message: Message):

    # فقط ادمین
    if message.from_user.id != ADMIN_ID:
        return

    parts = message.text.split()

    if len(parts) < 3:
        await message.answer("❗ فرمت درست:\n/giveref <user_id> <count | set X>")
        return

    target_id = int(parts[1])
    action = parts[2]

    async with AsyncSessionLocal() as session:
        user = await session.get(User, target_id)

        if not user:
            await message.answer("❌ کاربر در دیتابیس پیدا نشد.")
            return

        # حالت set
        if action == "set":
            if len(parts) < 4:
                await message.answer("❗ فرمت درست:\n/giveref <user_id> set <number>")
                return

            new_value = int(parts[3])
            user.referrals_count = new_value

            await session.commit()
            await message.answer(f"✅ مقدار رفرال کاربر {target_id} روی {new_value} تنظیم شد.")
            return

        # حالت add/remove
        try:
            amount = int(action)
        except:
            await message.answer("❗ مقدار باید عدد باشد.")
            return

        user.referrals_count += amount

        if user.referrals_count < 0:
            user.referrals_count = 0

        await session.commit()

        await message.answer(
            f"✅ رفرال کاربر {target_id} تغییر کرد.\n"
            f"🔢 مقدار جدید: {user.referrals_count}"
        )
