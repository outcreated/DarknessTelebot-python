import datetime
from opcode import stack_effect
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

class CreatePromocode(StatesGroup):
    promo_name = State()
    promo_uses = State()
    promo_duration = State()
    promo_end_date = State()
    product_id = State()
    message_id = 0
    

@state_router.callback_query(F.data == "a_create_promocode")
async def create_promocode(c: CallbackQuery, state: FSMContext):
    await state.set_state(CreatePromocode.promo_name)
    await c.message.edit_text(text="Введите название промокода")
    await state.update_data(message_id=c.message.message_id)

    

@state_router.message(CreatePromocode.promo_name)
async def create_promocode_name(m: Message, state: FSMContext):
    data = await state.get_data()
    promo = await requests_promocode.get_promocode_by_name(m.text)

    if promo:
        if promo.status:
            await m.bot.edit_message_text(message_id=data['message_id'], chat_id=m.from_user.id, text="Такой промокод уже существует. Измените название промокода")
        else:
            await state.update_data(promo_name=m.text)
            await state.set_state(CreatePromocode.promo_uses)
            await m.bot.edit_message_text(message_id=data['message_id'], chat_id=m.from_user.id,  text="Введите количество использований для промокода")
            await m.bot.delete_message(m.chat.id, m.message_id)
    else:
        await state.update_data(promo_name=m.text)
        await state.set_state(CreatePromocode.promo_uses)
        await m.bot.edit_message_text(message_id=data['message_id'], chat_id=m.from_user.id,  text="Введите количество использований для промокода")
        await m.bot.delete_message(m.chat.id, m.message_id)

@state_router.message(CreatePromocode.promo_uses)
async def create_promo_uses(m: Message, state: FSMContext):
    data = await state.get_data()
    await m.bot.edit_message_text(message_id=data['message_id'], chat_id=m.from_user.id,  text="Введите время, на которое промокод будет выдавать продукт\n\n1 час - 1h\n1 день - 1d\n1 месяц - 1m")
    await state.update_data(promo_uses=m.text)
    await state.set_state(CreatePromocode.promo_duration)
    await m.bot.delete_message(m.chat.id, m.message_id)

@state_router.message(CreatePromocode.promo_duration)
async def create_promo_duration(m: Message, state: FSMContext):
    data = await state.get_data()
    await m.bot.edit_message_text(message_id=data['message_id'], chat_id=m.from_user.id,  text="Введите время действия промокода\n\n1 час - 1h\n1 день - 1d\n1 месяц - 1m")
    await state.update_data(promo_duration=m.text)
    await state.set_state(CreatePromocode.promo_end_date)
    await m.bot.delete_message(m.chat.id, m.message_id)

@state_router.message(CreatePromocode.promo_end_date)
async def create_promo_end_date(m: Message, state: FSMContext):
    #    promo_name = State()
    #    promo_uses = State()
    #    promo_duration = State()
    #    promo_end_date = State()
    #    product_id = State()

    
    
    await state.update_data(promo_end_date=m.text)
    data = await state.get_data()
    await state.set_state(CreatePromocode.product_id)
    await m.bot.delete_message(m.chat.id, m.message_id)
    await m.bot.edit_message_text(message_id=data['message_id'], chat_id=m.from_user.id,  
                                  text="Выберите продукт, для которого хотите создать промокод",
                                  reply_markup=await ikb.create_promocode_product_selection_keyboard(data['promo_name'], data['promo_uses'], data['promo_duration'], data['promo_end_date']))

@state_router.message(CreatePromocode.product_id)
async def create_promo_product_id(m: Message, state: FSMContext):
    data = await state.get_data()

    await state.update_data(product_id=m.text)
    await state.clear()
    await m.bot.delete_message(m.chat.id, m.message_id)



@state_router.callback_query(F.data == "user_activate_promocode")
async def user_activate_promocode(c: CallbackQuery, state: FSMContext):
    await state.set_state(UsePromocodeState.name)
    await c.message.edit_text(text="Введите промокод")

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
    
    await state.clear()

async def timestamp_to_sub_end_date(timestamp: int) -> str:
    current_datetime = datetime.datetime.fromtimestamp(timestamp)
    return current_datetime.strftime('%d-%m-%Y | %H:%M:%S')

