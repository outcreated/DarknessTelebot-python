from database.database_core import User
from sqlalchemy.ext.asyncio import async_session
from database.database_core import async_session
from sqlalchemy import select

async def add_user(telegram_id: int, username: str, referrer_id: int) -> bool:
    async with async_session() as s:
        user = await s.scalar(select(User).where(User.telegram_id == telegram_id))

        if not user:
            user = User(telegram_id=telegram_id, username=username, referrer_id=referrer_id)
            s.add(user)
            await s.commit()
            return True
        else:
            return False
    
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
    