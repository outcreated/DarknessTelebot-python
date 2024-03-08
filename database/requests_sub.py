import time

from database.database_core import User, SubscriptionPattern
from sqlalchemy.ext.asyncio import async_session
from database.database_core import async_session, UserSubscription
from sqlalchemy import select


async def get_all_users_subscriptions() -> tuple[UserSubscription]:
    async with async_session() as session:
        return await session.scalars(select(UserSubscription))


async def delete_user_subscription(subscription_id):
    async with async_session() as session:
        subcription = await session.scalar(select(UserSubscription).where(UserSubscription.id == subscription_id))
        await session.delete(subcription)
        await session.commit()


async def get_user_subscriptions(telegram_id: int) -> tuple[UserSubscription]:
    async with async_session() as session:
        return await session.scalars(select(UserSubscription).where(UserSubscription.telegram_id == telegram_id))


async def get_subscription_by_id(id: int) -> SubscriptionPattern:
    async with async_session() as session:
        return await session.scalar(select(SubscriptionPattern).where(SubscriptionPattern.id == id))


async def get_product_subscriptions_patterns(product_id: int) -> tuple[SubscriptionPattern]:
    async with async_session() as session:
        return await session.scalars(select(SubscriptionPattern).where(SubscriptionPattern.product_id == product_id))


async def add_subscription_to_user(subscription_id: int, telegram_id: int) -> None:
    async with async_session() as session:
        subscription_pattern = await session.scalar(
            select(SubscriptionPattern).where(SubscriptionPattern.id == subscription_id))
        subcription = await session.scalar(select(UserSubscription).where(UserSubscription.telegram_id == telegram_id))

        if not subcription:
            subcription = UserSubscription(
                telegram_id=telegram_id,
                end_date=int(time.time()) + subscription_pattern.duration,
                product_id=subscription_pattern.product_id
            )
            session.add(subcription)
        else:
            subcription.end_date += subscription_pattern.duration
            await session.merge(subcription)
        await session.commit()

async def add_subscription_hours_to_user(hours: int, telegram_id: int, product_id: int) -> bool:
    async with async_session() as session:
        subcription = await session.scalar(select(UserSubscription).where(UserSubscription.telegram_id == telegram_id))

        if not subcription:
            subcription = UserSubscription(
                telegram_id=telegram_id,
                end_date=int(time.time()) + (hours * 60 * 60),
                product_id=product_id
            )
            session.add(subcription)
        else:
            subcription.end_date += (hours * 60 * 60)
            await session.merge(subcription)
        await session.commit()
        return True
