import telebot
import asyncio
import logging
import sys

def init() -> None:
    logging.basicConfig(level=logging.INFO,
                        stream=sys.stdout,
                        format=str("[time]") +
                        '[%(levelname)s] [%(name)s] %(message)s')
    asyncio.run(telebot.startBot())

init()