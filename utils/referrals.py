from database.models import AsyncSessionLocal, User

async def decrease_referral(user_id: int, amount: int = 1):
    async with AsyncSessionLocal() as session:
        user = await session.get(User, user_id)
        if not user:
            return False

        if user.referrals_count < amount:
            return False

        user.referrals_count -= amount
        await session.commit()
        return True
