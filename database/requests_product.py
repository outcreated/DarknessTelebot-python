from database.database_core import User
from sqlalchemy.ext.asyncio import async_session
from database.database_core import async_session, Product
from sqlalchemy import select

async def get_product_by_id(product_id) -> Product:
    async with async_session() as session:
        return await session.scalar(select(Product).filter_by(id = product_id))