# middlewares/antispam.py
import time
from aiogram import BaseMiddleware
from aiogram.types import Message

class AntiSpamMiddleware(BaseMiddleware):
    def __init__(self, limit: float = 0.7):
        super().__init__()
        self.limit = limit
        self.last_message_time = {}

    async def __call__(self, handler, event: Message, data):
        user_id = event.from_user.id
        now = time.time()

        last_time = self.last_message_time.get(user_id, 0)

        # اگر فاصله پیام‌ها کمتر از limit باشد → اسپم
        if now - last_time < self.limit:
            return  # پیام را نادیده بگیر

        self.last_message_time[user_id] = now
        return await handler(event, data)
