import config

from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from routers.commands_router import check_user_channel_subscribed, preRegisterUsers, generate_user_text_profile
from database import requests_user, requests_promocode, requests_product
from database.database_core import User, Promocode
from data import ikb

callback_router = Router()

@callback_router.callback_query(F.data == "check_preregister_subscribed")
async def register_of_button(c: CallbackQuery):
    if await check_user_channel_subscribed(c.from_user.id, c.bot):
        await c.answer("✅ Спасибо за подписку, провожу регистрацию...", show_alert=False, cache_time=2)
        status = await requests_user.add_user(c.from_user.id, c.from_user.username, preRegisterUsers[c.from_user.id])
        preRegisterUsers.pop(c.from_user.id)
        if status:
            await c.message.answer("Вы успешно зарегистрировались! Чтобы открыть главное меню бота, напишите /menu")
        else:
            await c.message.answer("Вы уже зарегистрирваны!")

        await c.bot.delete_message(c.from_user.id, c.message.message_id)
        
    else:
        await c.answer("❌ Вы не подписаны на канал", show_alert=False, cache_time=2)

@callback_router.callback_query(F.data == "main_menu")
async def open_main_menu(c: CallbackQuery):
    user = await requests_user.get_user_by_telegram_id(c.from_user.id)
    await c.message.edit_text(text=await generate_user_text_profile(user), reply_markup=ikb.main_menu_keyboard(user))


@callback_router.callback_query(F.data == "user_refsystem_menu")
async def open_refsystem_menu(c: CallbackQuery):
    user = await requests_user.get_user_by_telegram_id(c.from_user.id)
    await c.message.edit_text(text=await generate_refsystem_menu_text(user), reply_markup=ikb.referal_menu_keyboard())


@callback_router.callback_query(F.data == "user_promocode_menu")
async def open_promocode_menu(c: CallbackQuery):
    user = await requests_user.get_user_by_telegram_id(c.from_user.id)
    await c.message.edit_text(text=await generate_promocode_menu_text(user), reply_markup=ikb.promocode_menu_keyboard())

async def generate_refsystem_menu_text(user: User) -> str:
    text = f"""
    ► [ 🎁 Реферальная система ]
        ➖➖➖➖➖➖➖➖➖➖
        ► [ 🧩 ] Рефералов > <code>{len(user.get_referals())}</code>
        ► [ 💰 ] Баланс > <code>{user.balance} $</code>
        ► [ 💵 ] Общая прибыль > <code>{user.total_balance} $</code>
        ► [ 🎯 ] Ваш процент > <code>{user.ref_percentage}%</code>
        ► [ 📎 ] Ссылка > <a href='{config.REF_LINK_PATTERN + str(user.telegram_id)}'>(ПКМ > Копировать)</a>
        ➖➖➖➖➖➖➖➖➖➖
► [ 📩 Информация ]
        ➖➖➖➖➖➖➖➖➖➖
        ► <strong>B данном разделе вы можете посмотреть свою историю активированных промокодов и активировать промокод</strong>
    """

    return text

async def generate_promocode_menu_text(user: User) -> str:
    promocodes_id = user.get_promocodes()
    text = f"""► [ 🎁 Промокоды ]
        ➖➖➖➖➖➖➖➖➖➖    
        Последние <i>10</i> использованных промокодов:
    """
    if len(promocodes_id) < 1:
        text += f"""
        ► <i><b>Пусто</b></i>
        """
        return text
    
    for i in range(len(promocodes_id)):
        promocode = await requests_promocode.get_promocode_by_id(promocodes_id[i])
        product = await requests_product.get_product_by_id(promocode.product_id)
        text += f"\n    ► <i>#{promocode.name}</i> - <b>{product.name}</b> на <code>{promocode.product_duration/3600}</code><b> час(ов)</b>"

    return text