import asyncio
import logging
import os
import sys
import threading
import time

from colorama import Fore
import telebot

from aiogram import Bot
from dotenv import load_dotenv, find_dotenv

from tools import get_log_time
import server
import product_manager


'''
    Привет, разработчик.
    Если ты читаешь эти строчки, то ты редактируешь моего бота
    Я - Java программист, но когда писал данного бота только изучал Python

    Если тебе что-то непонятно из моего кода,
    то ты всегда можешь обратится ко мне

    Мои контакты:
    Telegram: @neverlessy или @outcreated
    VK: @neverlessy
    GitHub: @outcreated

    Заранее извиняюсь за местами плохой код, я новичок в данном ЯП
    Честно, я старался соблюдать E501, но иногда я все таки забивал на это
    Так что в коде присутствуют нарушения E501
'''


def init():
    server.init()
    product_manager.init()
    load_dotenv(find_dotenv())
    bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"), parse_mode="HTML")

    logging.basicConfig(level=logging.INFO,
                        stream=sys.stdout,
                        format=str(get_log_time()) +
                        '[%(levelname)s] [%(name)s] %(message)s')

    asyncio.run(telebot.start(bot))


init()
