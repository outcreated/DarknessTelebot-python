
import datetime
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

# Создаем асинхронный движок базы данных
DB_URL = 'postgresql+asyncpg://username:password@localhost/database_name'
async_engine = create_async_engine(DB_URL, echo=True, future=True)

# Создаем базовую модель
Base = declarative_base()

# Модель User


class User(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True)
    username = Column(String)
    referal_balance = Column(Integer)
    register_date = Column(
        String, default=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    products = relationship('Product')
    referals = Column(String)

    def __repr__(self):
        return f"User(user_id={self.user_id}, telegram_id={self.telegram_id}, username={self.username}, referal_balance={self.referal_balance}, register_date={self.register_date}, products={self.products}, referals={self.referals})"

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'telegram_id': self.telegram_id,
            'username': self.username,
            'referal_balance': self.referal_balance,
            'register_date': self.register_date,
            'products': [product.to_dict() for product in self.products],
            'referals': self.referals
        }

# Модель Product


class Product(Base):
    __tablename__ = 'products'
    product_id = Column(Integer, primary_key=True)
    product_name = Column(String)
    product_description = Column(String)
    product_photo = Column(String)
    product_active = Column(Boolean)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    product_variants = relationship('ProductVariant')

    def __repr__(self):
        return f"Product(product_id={self.product_id}, product_name={self.product_name}, product_description={self.product_description}, product_photo={self.product_photo}, product_active={self.product_active}, user_id={self.user_id}, product_variants={self.product_variants})"

    def to_dict(self):
        return {
            'product_id': self.product_id,
            'product_name': self.product_name,
            'product_description': self.product_description,
            'product_photo': self.product_photo,
            'product_active': self.product_active,
            'user_id': self.user_id,
            'product_variants': [variant.to_dict() for variant in self.product_variants]
        }

# Модель ProductVariant


class ProductVariant(Base):
    __tablename__ = 'product_variants'
    product_payment_id = Column(Integer, primary_key=True)
    product_payment_cost = Column(Integer)
    product_payment_duration = Column(Integer)
    product_id = Column(Integer, ForeignKey('products.product_id'))

    def __repr__(self):
        return f"ProductVariant(product_payment_id={self.product_payment_id}, product_payment_cost={self.product_payment_cost}, product_payment_duration={self.product_payment_duration}, product_id={self.product_id})"

    def to_dict(self):
        return {
            'product_payment_id': self.product_payment_id,
            'product_payment_cost': self.product_payment_cost,
            'product_payment_duration': self.product_payment_duration,
            'product_id': self.product_id
        }

# Создаем таблицы в базе данных


async def create_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Создаем сессию для работы с базой данных


async def create_session():
    session = sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False)
    async with session() as async_session:
        yield async_session

# Пример использования моделей


async def example_usage():
    async with create_session() as session:
        # Создание пользователей
        user1 = User(telegram_id=1, username='user1', referal_balance=100)
        user2 = User(telegram_id=2, username='user2', referal_balance=200)

        # Создание продуктов
        product1 = Product(product_name='Product 1', product_description='Description 1',
                           product_photo='photo1.jpg', product_active=True)
        product2 = Product(product_name='Product 2', product_description='Description 2',
                           product_photo='photo2.jpg', product_active=False)

        # Создание вариантов продуктов
        variant1 = ProductVariant(
            product_payment_cost=10, product_payment_duration=30)
        variant2 = ProductVariant(
            product_payment_cost=20, product_payment_duration=60)

        # Связываем продукты с пользователями
        user1.products.append(product1)
        user2.products.append(product2)

        # Связываем варианты продуктов с продуктами
        product1.product_variants.append(variant1)
        product2.product_variants.append(variant2)

        # Добавляем объекты в сессию
        session.add_all([user1, user2, product1, product2, variant1, variant2])

        # Записываем изменения в базу данных
        await session.commit()

        # Получение пользователей из базы данных
        users = await session.execute(User.select())
        for user in users.scalars():
            print(user.to_dict())

        # Получение продуктов из базы данных
        products = await session.execute(Product.select())
        for product in products.scalars():
            print(product.to_dict())

        # Получение вариантов продуктов из базы данных
        variants = await session.execute(ProductVariant.select())
        for variant in variants.scalars():
            print(variant.to_dict())

# Запуск примера использования моделей


async def main():
    await create_tables()
    await example_usage()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())

# В данном примере мы использовали библиотеку SQLAlchemy для создания моделей User, Product и ProductVariant. Каждая модель определена как класс, который наследуется от базового класса `Base`. Каждая модель имеет свои столбцы, а также отношения с другими моделями с помощью соответствующих свойств и атрибутов.

# Модели также имеют методы `__repr__`, которые возвращают строковое представление объектов модели, и метод
