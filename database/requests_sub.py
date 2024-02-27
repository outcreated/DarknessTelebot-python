from database.database_core import User
from sqlalchemy.ext.asyncio import async_session
from database.database_core import async_session, UserSubscription
from sqlalchemy import select

async def get_user_subscriptions(telegram_id: int) -> tuple[UserSubscription]:
    async with async_session() as session:
        return await session.scalars(select(UserSubscription).where(UserSubscription.telegram_id == telegram_id))