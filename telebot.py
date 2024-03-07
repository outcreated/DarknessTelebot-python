import config
import oc

from server import product_manager
from database import database_core
from routers import callbacks_router, commands_router, state_router
from colorama import Fore as fr
from aiogram import Bot, Dispatcher, __api_version__
from aiogram.enums import ParseMode
from cryptobot import init as cryptobot_init


async def startBot() -> None:
    oc.log("info",
           f"Запуск {fr.LIGHTMAGENTA_EX}Darkness System{fr.RESET} | Версия Aiogram: {fr.LIGHTRED_EX}{__api_version__}{fr.RESET}")
    await configure()
    await cryptobot_init()
    await product_manager.init_product_manager()
    bot = Bot(config.BOT_TOKEN, parse_mode=ParseMode.HTML)

    dp = Dispatcher()
    dp.include_routers(
        commands_router.command_router,
        callbacks_router.callback_router,
        state_router.state_router)

    await bot.delete_webhook(True)
    oc.log("info", "Бот успешно запущен")
    await dp.start_polling(bot)


async def configure():
    await database_core.init_database()
