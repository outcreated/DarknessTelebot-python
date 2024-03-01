from database.database_core import User, UserWithdrawMoney
from sqlalchemy.ext.asyncio import async_session
from database.database_core import async_session
from sqlalchemy import select

async def add_user(telegram_id: int, username: str, referrer_id: int) -> bool:
    async with async_session() as s:
        user = await s.scalar(select(User).where(User.telegram_id == telegram_id))

        if not user:
            user = User(telegram_id=telegram_id, username=username, referrer_id=referrer_id)
            s.add(user)
            if referrer_id != -1:
                referrer = await s.scalar(select(User).where(User.telegram_id == referrer_id))
                reflist = referrer.get_referals()
                reflist.append(telegram_id)
                referrer.set_referals(reflist)
                await s.merge(referrer)
            await s.commit()
            return True
        else:
            return False
        
async def add_referrer_balance(user: User, sum: float) -> None:
    async with async_session() as s:
        user = await s.scalar(select(User).where(User.telegram_id == user.referrer_id))
        user.balance = round((user.balance + (sum / user.ref_percentage)), 2)
        user.total_balance = round((user.total_balance + (sum / user.ref_percentage)), 2)
        await s.merge(user)
        await s.commit()
    
async def get_all_users() -> tuple[User]:
    async with async_session() as s:
        return await s.scalars(select(User))
    
async def get_user_by_telegram_id(telegram_id: int) -> User:
    async with async_session() as s:
        return await s.scalar(select(User).filter_by(telegram_id=telegram_id))
    
async def update_user(user: User) -> None:
    async with async_session() as s:
        await s.merge(user)
        await s.commit()

async def create_withdraw(telegram_id: int) -> None:
    async with async_session() as s:
        user = await s.scalar(select(User).where(User.telegram_id == telegram_id))
        userWithdraw = UserWithdrawMoney(telegram_id=telegram_id, amount=user.balance)

        if not await s.scalar(select(UserWithdrawMoney).where(UserWithdrawMoney.telegram_id == telegram_id)):
            s.add(userWithdraw)
            await s.commit()
            return True
        else:
            return False
    