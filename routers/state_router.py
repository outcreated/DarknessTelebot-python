import datetime
import time

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from routers.commands_router import check_user_channel_subscribed, preRegisterUsers, generate_user_text_profile
from database import requests_user, requests_promocode
from database.database_core import User
from data import ikb

state_router = Router()

class UsePromocodeState(StatesGroup):
    name = State()

@state_router.callback_query(F.data == "user_activate_promocode")
async def user_activate_promocode(c: CallbackQuery, state: FSMContext):
    await state.set_state(UsePromocodeState.name)
    await c.message.edit_text(text="Введите промокод")

    
'''
@state_router.message(UsePromocodeState.name)
async def activate_promocode(m: Message, state: FSMContext):
    response = await requests_promocode.activate_promocode(m.text, m.from_user.id)

    if response[0] == "PROMOCODE_EXPIRED":
        await m.answer("Срок действия данного промокода истек")
    elif response[0] == "PROMOCODE_ALREADY_USED":
        await m.answer("Вы уже использовали данный промокод")
    elif response[0] == "PROMOCODE_SUCCESS_USED":
        await m.answer(
            f"Вы успешно использовали промокод <i>{response[1]}</i> и получили лицензию на продукт <b>{response[2]}</b> до <code>{await timestamp_to_sub_end_date(response[3])}</code> ",
            reply_markup=ikb.activated_promocode_menu_keyboard())
    elif response[0] == "PROMOCODE_USES_LEFT_0":
        await m.answer("Данный промокод исчерпал количество активаций")
    elif response[0] == "PROMOCODE_NOT_FOUND":
        await m.answer("Данного промокода не существует")
    else:
        await m.answer("Произошла неизвестная ошибка, попробуйте позже или обратитесь к администратору") 
    
    print(response[0])
    await state.clear()
'''

@state_router.message(UsePromocodeState.name)
async def activate_promocode(m: Message, state: FSMContext):
    response = await requests_promocode.activate_promocode(m.text, m.from_user.id)
    response_message_map = {
        "PROMOCODE_EXPIRED": "Срок действия данного промокода истек",
        "PROMOCODE_ALREADY_USED": "Вы уже использовали данный промокод",
        "PROMOCODE_NOT_FOUND": "Данного промокода не существует",
        "PROMOCODE_USES_LEFT_0": "Данный промокод исчерпал количество активаций",
    }

    if response[0] in response_message_map:
        await m.answer(response_message_map[response[0]],
                       reply_markup=ikb.activated_promocode_menu_keyboard())
    elif response[0] == "PROMOCODE_SUCCESS_USED":
        await m.answer(
            f"Вы успешно использовали промокод <i>{response[1]}</i> и получили лицензию на продукт <b>{response[2]}</b> до <code>{await timestamp_to_sub_end_date(response[3])}</code>",
            reply_markup=ikb.activated_promocode_menu_keyboard())
    else:
        await m.answer("Произошла неизвестная ошибка, попробуйте позже или обратитесь к администратору")
    
    print(response[0])
    await state.clear()

async def timestamp_to_sub_end_date(timestamp: int) -> str:
    current_datetime = datetime.datetime.fromtimestamp(timestamp)
    return current_datetime.strftime('%d-%m-%Y | %H:%M:%S')

