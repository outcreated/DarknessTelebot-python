from aiogram import Router
from aiogram.types import CallbackQuery

callback_router = Router()

@callback_router.callback_query()
async def callback_query_handler(c: CallbackQuery):
    pass