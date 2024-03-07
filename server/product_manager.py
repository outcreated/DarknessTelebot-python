import threading
import time
import asyncio

from database import requests_sub


async def init_product_manager():
    new_loop = asyncio.new_event_loop()
    t = threading.Thread(target=thread_target, args=(new_loop,)).start()


async def async_task():
    while True:
        subscriptions = await requests_sub.get_all_users_subscriptions()
        for sub in subscriptions:
            if sub.end_date < int(time.time()):
                await requests_sub.delete_user_subscription(sub.id)
        await asyncio.sleep(1)


def thread_target(loop):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(async_task())
