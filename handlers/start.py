from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

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

    await message.answer(
        "👋 خوش آمدید",
        reply_markup=main_menu
    )