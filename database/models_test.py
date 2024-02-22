import datetime
from sqlalchemy import ForeignKey, PickleType, ForeignKey, PickleType
from sqlalchemy.orm import relationship, Mapped, mapped_column, DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, AsyncAttrs
from sqlalchemy.ext.asyncio import async_sessionmaker

engine = create_async_engine("sqlite+aiosqlite:///db.sqlite3")


async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    user_id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(unique=True)
    username: Mapped[str] = mapped_column()
    referal_balance: Mapped[int] = mapped_column()
    register_date: Mapped[str] = mapped_column(
        default=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    current_products: Mapped[dict] = mapped_column(PickleType)
    referals: Mapped[str] = mapped_column()


class Product(Base):
    __tablename__ = 'products'

    product_id: Mapped[int] = mapped_column(primary_key=True)
    product_name: Mapped[str] = mapped_column()
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


async def init_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)



from sqlalchemy import BigInteger, PickleType, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine("sqlite+aiosqlite:///db.sqlite3")

async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'
    user_id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id = mapped_column(BigInteger)
    current_products: Mapped[dict] = mapped_column(PickleType)
    # referral_id = mapped_column(ForeignKey('users.user_id'))
    # referrals = relationship('User', backref='referrer', remote_side=[user_id])
    # current_products: Mapped[dict] = mapped_column(PickleType)


class Product(Base):
    __tablename__ = 'products'
    product_id: Mapped[int] = mapped_column(primary_key=True)
    product_name: Mapped[str] = mapped_column()
    product_description: Mapped[str] = mapped_column()


class Payment(Base):
    __tablename__ = 'payments'
    product_payment_id: Mapped[int] = mapped_column(primary_key=True)
    product_payment_cost: Mapped[int] = mapped_column()
    product_payment_duration: Mapped[int] = mapped_column()

    product_id = mapped_column(ForeignKey('products.product_id'))
    product = relationship('Product', backref='payments')


async def init_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
