import asyncio
import config
from routers import callbacks_router, commands_router

from aiogram import Router, Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder

async def startBot() -> None:
    bot = Bot(config.BOT_TOKEN, parse_mode=ParseMode.HTML)
    
    dp = Dispatcher()
    dp.include_routers(commands_router.command_router, callbacks_router.callback_router)

    await bot.delete_webhook(True)
    await dp.start_polling(bot)

