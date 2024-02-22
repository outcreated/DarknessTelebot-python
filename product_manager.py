import asyncio
import threading
import time
from database import requests


def init():
    thread = threading.Thread(target=create)
    thread.start()


def create():
    asyncio.run(timer())


async def timer():
    while True:
        time.sleep(3600)
        await requests.update_users_products()
