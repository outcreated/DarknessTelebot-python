import random
import string
import time
from typing import Optional
from database.models import ProductVariant, TempProductDescription, User, Promocode, Product, async_session
from sqlalchemy import select, Table, MetaData, inspect, text
from sqlalchemy.ext.asyncio import create_async_engine
from database.models import get_engine


async def get_users() -> tuple[User]:
    async with async_session() as session:
        result = await session.scalars(select(User))
        return result


async def get_user_by_telegram_id(telegram_id) -> User:
    async with async_session() as session:
        user = await session.scalar(select(User).filter_by(
            telegram_id=telegram_id))
        return user


async def get_products() -> tuple[Product]:
    async with async_session() as session:
        result = await session.scalars(select(Product))
        return result


async def get_product_by_name(product_name: str) -> Product:
    async with async_session() as session:
        product = await session.scalar(select(Product).filter_by(
            product_name=product_name
        ))
        return product


async def get_product_by_key(product_key: str) -> Product:
    async with async_session() as session:
        product = await session.scalar(select(Product).filter_by(
            product_key=product_key
        ))
        return product


async def get_product_by_id(product_id: int) -> Product:
    async with async_session() as session:
        product = await session.scalar(select(Product).filter_by(
            product_id=product_id
        ))
        return product


async def get_product_variants() -> tuple[ProductVariant]:
    async with async_session() as session:
        result = await session.scalars(select(ProductVariant))
        return result


async def get_product_variant_by_product_id(product_id: int) -> ProductVariant:
    async with async_session() as session:
        result = await session.scalar(select(ProductVariant).filter_by(
            product_id=product_id
        ))
        return result


async def get_temp_product_description() -> str:
    async with async_session() as session:
        result = await session.scalar(select(TempProductDescription))
        return result.description


async def set_temp_product_description(description: str):
    async with async_session() as session:
        session.add(TempProductDescription(description=description))
        await session.commit()


async def clear_temp_product_description():
    async with async_session() as session:
        query = str("DELETE FROM temp_product_description")
        await session.execute(text(query))
        await session.commit()


async def generate_product_key(length):
    characters = string.ascii_letters + string.digits
    key = ''.join(random.choice(characters) for _ in range(length))
    return key


async def set_product(product_name: str,
                      product_description: Optional[str] = "__empty__",
                      product_photo: Optional[str] = "no_photo",
                      product_active: Optional[bool] = False):
    async with async_session() as session:
        session.add(Product(product_key=await generate_product_key(32),
                            product_name=product_name,
                            product_description=product_description,
                            product_photo=product_photo,
                            product_active=product_active))
        await session.commit()


async def add_promocode_to_database(
        promocode_name: str,
        promocode_use_left: int,
        promocode_time_left: int,
        promocode_give_code: str
):
    async with async_session() as session:
        current_timestamp = int(time.time() * 1000)
        print(promocode_time_left)
        time_to = int(promocode_time_left) * 60000
        promocode_time_left = current_timestamp + time_to
        session.add(Promocode(
            promocode_name=promocode_name,
            promocode_use_left=promocode_use_left,
            promocode_time_left=promocode_time_left,
            promocode_players_used="",
            promocode_give_code=promocode_give_code

        ))
        await session.commit()


async def give_user_product(
        telegram_id: int,
        product_id: int,
        product_duration: int
):
    async with async_session() as session:
        user = await get_user_by_telegram_id(telegram_id)
        if user.current_products == "":
            new_product_str = "1:24"

            query = f"UPDATE users SET current_products = '{new_product_str}' "\
                f"WHERE telegram_id = '{telegram_id}'"
            await session.execute(text(query))
            await session.commit()
        else:
            h_left = int(user.current_products.split(":")[1])
            h_left += 24
            new_product_str = f"1:{h_left}"
            query = f"UPDATE users SET current_products = '{new_product_str}' "\
                f"WHERE telegram_id = '{telegram_id}'"
            await session.execute(text(query))
            await session.commit()


async def update_promocode(
        promocode_name: str,
        telegram_id: int
):
    async with async_session() as session:
        promocode = await session.scalar(
            select(Promocode)
            .where(Promocode.promocode_name == promocode_name))
        if not promocode:
            return "promo_not_exist"

        promocode_gc = promocode.promocode_give_code
        if promocode.promocode_use_left > 0 and promocode.promocode_time_left > int(time.time() * 1000):
            left = promocode.promocode_use_left - 1
            p_used = promocode.promocode_players_used.split("-")
            if not str(telegram_id) in p_used:
                players_used = promocode.promocode_players_used + \
                    f"-{telegram_id}"

                query = f"UPDATE promocodes SET promocode_use_left = {left}"\
                        f", promocode_players_used = '{players_used}' "\
                        f"WHERE promocode_name = '{promocode_name}'"
                await session.execute(text(query))
                await session.commit()
                return promocode_gc
            else:
                return "promo_used"
        else:
            query = f"DELETE FROM promocodes WHERE promocode_name = '{promocode_name}'"
            await session.execute(text(query))
            await session.commit()
            return "promo_not_exist"


async def update_user_hwid(hwid: str, telegram_id: int):
    async with async_session() as session:
        query = f"UPDATE users SET user_hwid = '{hwid}' WHERE telegram_id = '{telegram_id}'"
        await session.execute(text(query))
        await session.commit()


async def update_user_referals(telegram_id: int, referer_id: int):
    async with async_session() as session:
        print(str(telegram_id) + " : " + str(referer_id))
        user = await session.scalar(select(User).filter_by(
            telegram_id=referer_id
        ))
        referals = user.referals
        referals += (str(referer_id) + " ")
        query = f"UPDATE users SET referals = '{referals}' WHERE telegram_id = '{referer_id}'"
        await session.execute(text(query))
        await session.commit()


async def add_referer_balance(telegram_id: int):
    async with async_session() as session:
        user_referal = await session.scalar(select(User).filter_by(
            telegram_id=telegram_id
        ))

        if not user_referal.referer_id == 0:
            if not user_referal.referer_id == telegram_id:
                user_referer = await session.scalar(select(User).filter_by(
                    telegram_id=user_referal.referer_id
                ))
                tmpbalance = user_referer.referal_balance + 0.4
                query = f"UPDATE users SET referal_balance = '{tmpbalance}' WHERE telegram_id = '{user_referal.referer_id}'"
                await session.execute(text(query))
                await session.commit()


async def clear_referer_balance(telegram_id: int):
    async with async_session() as session:
        query = f"UPDATE users SET referal_balance = '0' WHERE telegram_id = '{telegram_id}'"
        await session.execute(text(query))
        await session.commit()


async def check_referer_balance(tg_id: int):
    async with async_session() as session:
        user = await session.scalar(select(User).filter_by(
            telegram_id=tg_id
        ))
        return user.referal_balance


async def update_users_products():
    async with async_session() as session:
        users = await get_users()
        for user in users:
            cp = user.current_products
            if cp == "":
                pass
            else:
                product_id = cp.split(":")[0]
                product_h = cp.split(":")[1]
                if int(product_h) <= 0:
                    query = f"UPDATE users SET current_products = '' WHERE telegram_id = '{user.telegram_id}'"
                    await session.execute(text(query))
                    await session.commit()
                else:
                    new_product_line = f"{str(product_id)}:{str(int(product_h)-1)}"
                    query = f"UPDATE users SET current_products = '{new_product_line}' WHERE telegram_id = '{user.telegram_id}'"
                    await session.execute(text(query))
                    await session.commit()


async def set_users(
        tg_id: int,
        username: Optional[str] = "_",
        referal_balance: Optional[int] = 0,
        current_products: Optional[str] = "",
        referals: Optional[str] = "",
        referer_id: Optional[int] = 0,
        user_hwid: Optional[str] = ""
):
    # user_id, telegram_id, username, referal_balance, current_products, referals
    async with async_session() as session:
        user = await session.scalar(select(User)
                                    .where(User.telegram_id == tg_id))

        if not user:
            session.add(
                User(
                    telegram_id=tg_id,
                    username=username,
                    referal_balance=referal_balance,
                    current_products=current_products,
                    referals=referals,
                    referer_id=referer_id,
                    user_hwid=user_hwid
                ))
            await session.commit()
