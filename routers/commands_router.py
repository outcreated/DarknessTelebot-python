
from data import ikb
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart

command_router = Router()

@command_router.message(CommandStart())
async def commandStartExecutor(m: Message) -> None:
    await m.answer("Крутая клавиатура!", reply_markup=ikb.ikbWebAppTest())