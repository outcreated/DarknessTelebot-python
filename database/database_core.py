from email.policy import default
import config
import asyncio
import oc
import time
import json
from sqlalchemy import BigInteger, Integer, String, Boolean, ForeignKey, Float, ARRAY
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, async_sessionmaker, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
   
engine = create_async_engine(config.DATABASE_URL, echo=False, future=True)
Base = declarative_base()
async_session = async_sessionmaker(engine)

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    username: Mapped[str] = mapped_column(String)
    ref_percentage: Mapped[int] = mapped_column(Integer, default=10)
    balance: Mapped[float] = mapped_column(Float, default=0.0)
    total_balance: Mapped[float] = mapped_column(Float, default=0.0)
    register_date: Mapped[int] = mapped_column(BigInteger, default=int(time.time()))
    isAdmin: Mapped[bool] = mapped_column(Boolean, default=False)
    referrer_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.telegram_id"), default=-1)
    referals: Mapped[str] = mapped_column(String, default="")
    promocodes_used: Mapped[str] = mapped_column(String, default="")
    hwid: Mapped[str] = mapped_column(String, default="@")

    def set_referals(self, referals):
        self.referals = json.dumps(referals)

    def get_referals(self):
        return json.loads(self.referals) if self.referals else []
    
    def get_promocodes(self, promocodes_used):
        self.promocodes_used = json.dumps(promocodes_used)

    def set__promocodes(self):
        return json.loads(self.promocodes_used) if self.promocodes_used else []

class Product(Base):
    __tablename__ = "products"

    id = mapped_column(Integer, primary_key=True, index=True)
    name = mapped_column(String, index=True)
    uuid = mapped_column(String, unique=True)
    description = mapped_column(String)
    status = mapped_column(Boolean, default=False)

    subscriptions = relationship("Subscription", back_populates="product")

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = mapped_column(Integer, primary_key=True, index=True)
    product_id = mapped_column(Integer, ForeignKey("products.id"))
    duration = mapped_column(Integer)
    price = mapped_column(Integer)
    user_id = mapped_column(Integer)

    product = relationship("Product", back_populates="subscriptions")

async def init_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        oc.log("info", "База данных успешно загружена")

async def get_engine() -> AsyncEngine:
    return engine
