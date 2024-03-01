import config
import cryptobot

from aiogram import Router, F
from aiogram.types import CallbackQuery
from routers.commands_router import check_user_channel_subscribed, preRegisterUsers, generate_user_text_profile
from database import requests_user, requests_promocode, requests_product, requests_sub
from database.database_core import Product, User, Promocode
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

@callback_router.callback_query(F.data == "user_product_menu")
async def open_product_menu(c: CallbackQuery):
    products = await requests_product.get_all_products()

    await c.message.edit_text(text=await generate_product_menu_text(), reply_markup=ikb.product_menu_keyboard(products))

@callback_router.callback_query(F.data.startswith("user_product_menu@"))
async def open_product_menu_by_id(c: CallbackQuery):
    product = await requests_product.get_product_by_id(int(c.data.split("@")[1]))
    product_subs = await requests_sub.get_product_subscriptions_patterns(product.id)
    await c.message.edit_text(
        text=await generate_current_product_menu_text(product), 
        reply_markup=ikb.current_product_menu_keyboard(product_subs))
    
@callback_router.callback_query(F.data.startswith("user_buy_subscription@"))
async def user_buy_subscription(c: CallbackQuery):
    subscription_id = int(c.data.split("@")[1])
    subscription = await requests_sub.get_subscription_by_id(subscription_id)

    url = await cryptobot.create_invoice(subscription.cost, c.from_user.id, subscription.id)
    await c.message.edit_text(await generate_buy_subscription_text(),
                              reply_markup=ikb.crypto_bot_pay_keyboard(url))
    
@callback_router.callback_query(F.data == "update_invoice_status")
async def update_invoice_status(c: CallbackQuery):
    status = await cryptobot.update_invoice(c.from_user.id)

    if status[0] == "active":
        await c.answer("❌ Счет не оплачен", cache_time=5)
    elif status[0] == "paid":
        await c.answer("✅ Оплата прошла успешно!")
        await cryptobot.delete_invoice(c.from_user.id)
        user = await requests_user.get_user_by_telegram_id(c.from_user.id)
        subscription = await requests_sub.get_subscription_by_id(status[1])
        await requests_user.add_referrer_balance(user, subscription.cost)
        await requests_sub.add_subscription_to_user(status[1], c.from_user.id)
        await c.message.edit_text(text=await generate_user_text_profile(user), 
                                  reply_markup=ikb.main_menu_keyboard(user))
        
@callback_router.callback_query(F.data == "user_cancel_buy_subscription")
async def user_cancel_buy_subscription(c: CallbackQuery):
    user = await requests_user.get_user_by_telegram_id(c.from_user.id)
    await cryptobot.delete_invoice(c.from_user.id)
    await c.answer("❌ Оплата отменена", cache_time=5)
    await c.message.edit_text(text=await generate_user_text_profile(user), 
                              reply_markup=ikb.main_menu_keyboard(user))
    
@callback_router.callback_query(F.data == "user_ref_withdraw_money")
async def user_ref_withdraw_money(c: CallbackQuery):
    user = await requests_user.get_user_by_telegram_id(c.from_user.id)
    if user.balance <= 5.0:
        await c.answer("\t\tНедостаточно средств\n\nМинимальная сумма для вывода: 5.0 $",
                       show_alert=True)
        return
    status = await requests_user.create_withdraw(c.from_user.id)

    if not status:
        await c.answer("❌ У вас уже есть активная заявка на вывод, ожидайте",
                       show_alert=True)
    else:
        await c.answer("✅ Вы успешно отправили заявку на вывод!\n\nОжидайте ответ от администратора",
                       show_alert=True)
        
@callback_router.callback_query(F.data == "user_settings_menu")
async def user_settings_menu(c: CallbackQuery):
    await c.message.edit_text(text="Настройки. Все", reply_markup=ikb.settings_menu_keyboard())

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

async def generate_product_menu_text() -> str:
    return """► [ 💠 Товары ]
        ➖➖➖➖➖➖➖➖➖➖    
        B данном разделе вы можете приобрести или продлить подписку для различных продуктов
    """

async def generate_current_product_menu_text(product: Product) -> str:
    text = f"""► [ 🔑 Меню товара ]
        ➖➖➖➖➖➖➖➖➖➖    
        Название товара: <code>{product.name}</code>
        Описание товара: <code>{product.description}</code>
        Версия: <code>{product.version}</code>
        ➖➖➖➖➖➖➖➖➖➖    

► [ 📩 Информация ]
        ➖➖➖➖➖➖➖➖➖➖
        ► <strong>При нажатии на кнопки ниже автоматически будет создан счет в <i>Crypto Bot</i></strong> 
        ► <strong>Чтобы приобрести продукт оплатите счет</strong>               
    """

    return text

async def generate_buy_subscription_text() -> str:
    return "Для того, чтобы купить данный продукт оплатите счет в <i>CryptoBot</i>\n " \
           "У вас есть 5 минут на оплату, после чего счет <strong>перестанет существовать</strong> и при попытке его "\
           "пополнить вы потеряете деньги и не получите ничего\n\n<strong>Рекомендуем</strong> указывать свой <i>Telegram ID</i> в коментарии к платежу"