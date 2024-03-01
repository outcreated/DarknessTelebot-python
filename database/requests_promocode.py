import time
import re
from typing import Optional
from database.database_core import Promocode, User, Product
from sqlalchemy.ext.asyncio import async_session
from database.database_core import async_session, UserSubscription
from sqlalchemy import select

time_multipliers = {
    "M": 60,
    "H": 3600,
    "D": 86400
}

async def get_promocode_by_id(promocode_id: int) -> Promocode:
    async with async_session() as session:
        return await session.scalar(select(Promocode).where(Promocode.id == promocode_id))

async def add_promocode(
        promocode_name: str, 
        promocode_uses: int,
        promocode_end_date: str,
        promocode_product_id: int,
        promocode_product_duration: int,
        promocode_description: Optional[str] = ""
        ) -> bool:
    async with async_session() as session:
        promocode = await session.scalar(select(Promocode).where(Promocode.name == promocode_name))

        if not promocode: 
            delay, type

            try:
                delay, type = date_split(promocode_end_date)
            except IndexError as e:
                return False

            delay *= time_multipliers.get(type, 60000)

            
            promocode = Promocode(
                name=promocode_name, 
                uses_left=promocode_uses, 
                end_date=delay, 
                description=promocode_description,
                product_id=promocode_product_id,
                product_duration=promocode_product_duration
                )
            session.add(promocode)
            await session.commit()
            return True
        else:
            return False
        
async def activate_promocode(promocode_name: str, telegram_id) -> tuple: 
    async with async_session() as session:
        promocode = await session.scalar(select(Promocode).where(Promocode.name == promocode_name))
        user = await session.scalar(select(User).where(User.telegram_id == telegram_id))

        if promocode:
            if promocode.uses_left > 0:
                if promocode.end_date < int(time.time()):
                    return ("PROMOCODE_EXPIRED",)
                promocode.uses_left = promocode.uses_left - 1
                used_users = promocode.get_used_users()
                for user_promocode in used_users:
                    if user_promocode == telegram_id:
                        return ("PROMOCODE_ALREADY_USED",)
                used_users.insert(0, telegram_id)
                promocode.set_used_users(used_users)

                promocodes = user.get_promocodes()
                promocodes.insert(0, promocode.id)
                user.set_promocodes(promocodes)

                subcription = await session.scalar(select(UserSubscription).where(UserSubscription.telegram_id == telegram_id))
                product = await session.scalar(select(Product).where(Product.id == promocode.product_id))

                if not subcription:
                    subcription = UserSubscription(
                        telegram_id=telegram_id,
                        end_date=int(time.time()) + promocode.product_duration,
                        product_id=promocode.product_id
                        )
                    session.add(subcription)
                else:
                    subcription.end_date = int(time.time()) + ((subcription.end_date - int(time.time())) + promocode.product_duration)
                    await session.merge(subcription)

                dur = subcription.end_date
                product_name = product.name
                await session.merge(promocode)
                await session.merge(user)
                await session.commit()
                return ("PROMOCODE_SUCCESS_USED", "#" + promocode_name, product_name, dur)
            else:
                if promocode.status:
                    promocode.status = False
                    await session.merge(promocode)
                    await session.commit()
                    return ("PROMOCODE_USES_LEFT_0",)
                else:
                    return ("PROMOCODE_USES_LEFT_0",)

        else:
            return ("PROMOCODE_NOT_FOUND",)
        
def date_split(input_string):
    match = re.match(r"(\d+)(\w)", input_string)
    if match:
        return int(match.group(1)), str(match.group(2)).upper()
    else:
        return None, None