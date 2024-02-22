import os
import platform
from threading import Thread

from colorama import Fore
from tools import cis

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram import __api_version__
from aiogram import __version__
from dotenv import load_dotenv, find_dotenv
from database.models import init_database
import market

from handlers import register, admin, user

load_dotenv(find_dotenv())

dispatcher = Dispatcher()
bot = None
BOT_VERSION = os.getenv("BOT_VERSION")
BOT_CONSOLE_NAME = os.getenv("BOT_CONSOLE_NAME")


async def start(bot_telegram: Bot):
    await clear()
    print(
        f"Запуск {Fore.MAGENTA}{BOT_CONSOLE_NAME}{Fore.RESET} | "
        f"Версия бота: [{Fore.LIGHTCYAN_EX}{BOT_VERSION}{Fore.RESET}] | "
        f"Версия Telegram API: [{Fore.LIGHTGREEN_EX}{__api_version__}"
        f"{Fore.RESET}] | Версия "
        f"aiogram API: [{Fore.LIGHTYELLOW_EX}{__version__}{Fore.RESET}]\n")

    global bot
    bot = bot_telegram
    bot_thread = Thread(target=await init_bot())
    bot_thread.start()


async def init_bot():
    await init_database()
    dispatcher.include_routers(user.user_router,
                               register.register_router,
                               admin.admin_router)
    cis("Запуск бота")
    await market.init()
    await bot.delete_webhook(drop_pending_updates=True)
    # await bot.set_my_name("Outcreated Service")
    # await bot.set_my_short_description("Интернет магазин цифровых товаров")
    await bot.set_my_description(" Интернет магазин цифровых товаров\n\n"
                                 "- Парсеры\n- Скрипты\n- Услуги\n- Аккаунты"
                                 )
    await bot.set_my_commands([
        BotCommand(command="menu", description="Главное меню бота")])
    await dispatcher.start_polling(bot)


async def clear():
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')
