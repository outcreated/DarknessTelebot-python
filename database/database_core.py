import config
import asyncio
import oc
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
   
engine = create_async_engine(config.DATABASE_URL, echo=False, future=True)
Base = declarative_base()

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    uuid = Column(String, unique=True)
    description = Column(String)
    status = Column(Boolean, default=False)

    subscriptions = relationship("Subscription", back_populates="product")

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    duration = Column(Integer)
    price = Column(Integer)
    user_id = Column(Integer)

    product = relationship("Product", back_populates="subscriptions")

async def init_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        oc.log("info", "База данных успешно загружена")