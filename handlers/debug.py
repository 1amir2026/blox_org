from aiogram import Router
from aiogram.types import Message
router = Router()

@router.message(commands=["id"])
async def get_id(message: Message):
    await message.answer(f"Chat ID: {message.chat.id}")
