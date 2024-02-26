import config

from aiogram import Router, F
from aiogram.types import CallbackQuery
from routers.commands_router import check_user_channel_subscribed, preRegisterUsers, generate_user_text_profile
from database import requests_user
from database.database_core import User
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

async def generate_refsystem_menu_text(user: User) -> str:
    text = f"""
    ► [ 🎭 Реферальная система ]
        ➖➖➖➖➖➖➖➖➖➖
        ► [ 🧩 ] Рефералов > <code>{len(user.get_referals())}</code>
        ► [ 💰 ] Баланс > <code>{user.balance} $</code>
        ► [ 💵 ] Общая прибыль > <code>{user.total_balance} $</code>
        ► [ 🎯 ] Ваш процент > <code>{user.ref_percentage}%</code>
        ► [ 📎 ] Ссылка > <a href='{config.REF_LINK_PATTERN + str(user.telegram_id)}'>(ПКМ > Копировать)</a>
        ➖➖➖➖➖➖➖➖➖➖
► [ 📩 Информация ]
        ➖➖➖➖➖➖➖➖➖➖
        ► <strong>Для отдельных пользователей c большим количеством рефералов есть система повышения процента прибыли</strong>
    """

    return text

async def generate_promocode_menu_text(user: User) -> str:
    text = f"""
    ► [ 🎭 Реферальная система ]
        ➖➖➖➖➖➖➖➖➖➖
        ► [ 🧩 ] Рефералов > <code>{len(user.get_referals())}</code>
        ► [ 💰 ] Баланс > <code>{user.balance} $</code>
        ► [ 💵 ] Общая прибыль > <code>{user.total_balance} $</code>
        ► [ 🎯 ] Ваш процент > <code>{user.ref_percentage}%</code>
        ► [ 📎 ] Ссылка > <a href='{config.REF_LINK_PATTERN + str(user.telegram_id)}'>(ПКМ > Копировать)</a>
        ➖➖➖➖➖➖➖➖➖➖
► [ 📩 Информация ]
        ➖➖➖➖➖➖➖➖➖➖
        ► <strong>Для отдельных пользователей c большим количеством рефералов есть система повышения процента прибыли</strong>
    """

    return text