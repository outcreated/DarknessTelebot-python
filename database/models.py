import datetime
from sqlalchemy import ForeignKey, PickleType, BigInteger
from sqlalchemy.orm import relationship, Mapped, mapped_column, DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, AsyncAttrs, AsyncEngine
from sqlalchemy.ext.asyncio import async_sessionmaker

engine = create_async_engine("sqlite+aiosqlite:///db.sqlite3")


async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    user_id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    username: Mapped[str] = mapped_column()
    referal_balance: Mapped[float] = mapped_column()
    register_date: Mapped[str] = mapped_column(
        default=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    current_products: Mapped[str] = mapped_column()
    referals: Mapped[str] = mapped_column()
    referer_id: Mapped[int] = mapped_column(BigInteger)
    user_hwid: Mapped[str] = mapped_column()


class Product(Base):
    __tablename__ = 'products'

    product_id: Mapped[int] = mapped_column(primary_key=True)
    product_name: Mapped[str] = mapped_column()
    product_key: Mapped[str] = mapped_column()
    product_description: Mapped[str] = mapped_column()
    product_photo: Mapped[str] = mapped_column()
    product_active: Mapped[bool] = mapped_column()

    product_variants = relationship('ProductVariant')


class ProductVariant(Base):
    __tablename__ = 'product_variants'

    product_payment_id: Mapped[int] = mapped_column(primary_key=True)
    product_payment_cost: Mapped[int] = mapped_column()
    product_payment_duration: Mapped[int] = mapped_column()

    product_id: Mapped[int] = mapped_column(ForeignKey('products.product_id'))


class Promocode(Base):
    __tablename__ = 'promocodes'

    promocode_id: Mapped[int] = mapped_column(primary_key=True)
    promocode_name: Mapped[str] = mapped_column()
    promocode_use_left: Mapped[int] = mapped_column()
    promocode_time_left: Mapped[int] = mapped_column(BigInteger)
    promocode_players_used: Mapped[str] = mapped_column()
    promocode_give_code: Mapped[str] = mapped_column()


class TempProductDescription(Base):
    __tablename__ = 'temp_product_description'

    description_id: Mapped[int] = mapped_column(primary_key=True)
    description: Mapped[str] = mapped_column()


async def init_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_engine() -> AsyncEngine:
    return engine
