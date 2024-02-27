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

    def set_promocodes(self):
        return json.loads(self.promocodes_used) if self.promocodes_used else []
    
class Promocode(Base):
    __tablename__ = "promocodes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    # subscription_id: Mapped[int] = mapped_column(Integer, ForeignKey("subscriptions_types.id"))
    total_uses: Mapped[int] = mapped_column(Integer, default=0)
    uses_left: Mapped[int] = mapped_column(Integer, default=0)
    end_date: Mapped[int] = mapped_column(BigInteger, default=int(time.time()))
    description: Mapped[str] = mapped_column(String, default="")
    status: Mapped[bool] = mapped_column(Boolean, default=False)
    used_users: Mapped[str] = mapped_column(String, default="")

    def get_used_users(self, used_users):
        self.used_users = json.dumps(used_users)

    def set_used_users(self):
        return json.loads(self.used_users) if self.used_users else []

class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, default="")
    description: Mapped[str] = mapped_column(String, default="")
    version: Mapped[str] = mapped_column(String, default="1.0.0")
    active: Mapped[bool] = mapped_column(Boolean, default=False)

class SubscriptionPattern(Base):
    __tablename__ = "subscription_patterns"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cost: Mapped[float] = mapped_column(Float, default=0.0)
    duration: Mapped[int] = mapped_column(BigInteger, default=0)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey('products.id'))
    product: Mapped[Product] = relationship(Product)
    

class UserSubscription(Base):
    __tablename__ = "user_subscriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.telegram_id'))
    start_date: Mapped[int] = mapped_column(BigInteger, default=int(time.time()))
    end_date: Mapped[int] = mapped_column(BigInteger, default=0)
    user: Mapped[Product] = relationship(User)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey('products.id'))
    product: Mapped[Product] = relationship(Product)

async def init_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        oc.log("info", "База данных успешно загружена")

async def get_engine() -> AsyncEngine:
    return engine
