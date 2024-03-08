import config
import oc
import os
import datetime

from server import product_manager
from database import database_core
from routers import callbacks_router, commands_router, state_router
from colorama import Fore as fr
from aiogram import Bot, Dispatcher, __api_version__
from aiogram.enums import ParseMode
from cryptobot import init as cryptobot_init

from aiogram.fsm.context import FSMContext
from aiogram.types import Update
from aiogram.dispatcher.middlewares.base import BaseMiddleware
import logging
from typing import Callable, Any, Awaitable

log_path = "logs/latest.log"

# Функция для переименования существующего лога
def rename_old_log(log_path):
    if os.path.exists(log_path):
        base, extension = os.path.splitext(log_path)
        create_time = os.path.getctime(log_path)
        formatted_time = timestamp_to_date(int(create_time))
        new_name = f"logs/old/old_{formatted_time}{extension}"
        os.rename(log_path, new_name)

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseMiddleware):
    async def __call__(
            self, 
            handler: Callable[[Update, FSMContext], Awaitable[Any]], 
            event: Update, 
            data: dict
        ) -> Any:
        if event.callback_query:
            logger.fatal(f"CQ: {event.callback_query.data} | ID: {event.update_id} | USER: {event.callback_query.from_user.id}")
        return await handler(event, data)

async def startBot() -> None:
    rename_old_log(log_path)
    logging.basicConfig(filename=f'{log_path}', filemode='w', level=logging.FATAL,
                        format='[%(asctime)s]:[%(name)s] $%(funcName)s ~= %(message)s')
    oc.log("info",
           f"Запуск {fr.LIGHTMAGENTA_EX}Darkness System{fr.RESET} | Версия Aiogram: {fr.LIGHTRED_EX}{__api_version__}{fr.RESET}")
    await configure()
    await cryptobot_init()
    await product_manager.init_product_manager()
    bot = Bot(config.BOT_TOKEN, parse_mode=ParseMode.HTML)

    dp = Dispatcher()
    dp.update.outer_middleware.register(LoggingMiddleware())
    dp.include_routers(
        commands_router.command_router,
        callbacks_router.callback_router,
        state_router.state_router)

    await bot.delete_webhook(True)
    oc.log("info", "Бот успешно запущен")
    await dp.start_polling(bot)


async def configure():
    await database_core.init_database()

def timestamp_to_date(timestamp: int) -> str:
    current_datetime = datetime.datetime.fromtimestamp(timestamp)
    return current_datetime.strftime('%d-%m-%Y_%H-%M-%S')
