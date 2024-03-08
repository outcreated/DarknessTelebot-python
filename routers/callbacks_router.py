import time
import config
import cryptobot
import datetime
import logging
import shutil

from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from routers.commands_router import check_user_channel_subscribed, preRegisterUsers, generate_user_text_profile
from database import requests_user, requests_promocode, requests_product, requests_sub
from database.database_core import PaidInvoice, Product, User, Promocode
from data import ikb

callback_router = Router()
logger = logging.getLogger(__name__)


# ================================================================
# =====================USER=======================================
# ================================================================

@callback_router.callback_query(F.data == "check_preregister_subscribed")
async def register_of_button(c: CallbackQuery):
    if await check_user_channel_subscribed(c.from_user.id, c.bot):
        await c.answer("✅ Спасибо за подписку, провожу регистрацию...", show_alert=False, cache_time=2)
        status = await requests_user.add_user(c.from_user.id, c.from_user.username, preRegisterUsers[c.from_user.id])
        preRegisterUsers.pop(c.from_user.id)
        if status:
            await c.message.answer("Вы успешно зарегистрировались! Чтобы открыть главное меню бота, напишите /menu")
            logger.fatal(f"Пользователь [{c.from_user.username}] зарегистрирован | ID: [{c.from_user.id}]")
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


@callback_router.callback_query(F.data == "user_settings_menu")
async def user_settings_menu(c: CallbackQuery):
    await c.message.edit_text(text="Настройки. Все", reply_markup=ikb.settings_menu_keyboard())


@callback_router.callback_query(F.data == "user_subscriptions_menu")
async def user_subscriptions_menu(c: CallbackQuery):
    await c.message.edit_text(
        text=await generate_subscriptions_menu_text(c.from_user.id),
        reply_markup=await ikb.subscriptions_menu_keyboard(c.from_user.id))


@callback_router.callback_query(F.data.startswith("user_info_product@"))
async def user_info_product(c: CallbackQuery):
    product = await requests_product.get_product_by_id(int(c.data.split("@")[1]))
    await c.message.edit_text(text=await generate_product_info_menu_text(product),
                              reply_markup=await ikb.generate_product_info_menu_keyboard(product))


# ---------------------------------------------------
# ---------------------------------------------------

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
        
        logger.fatal(f"Пользователь [{c.from_user.id}] оплатил счет счет | ID: {status[1]}")


@callback_router.callback_query(F.data == "user_cancel_buy_subscription")
async def user_cancel_buy_subscription(c: CallbackQuery):
    user = await requests_user.get_user_by_telegram_id(c.from_user.id)
    await cryptobot.delete_invoice(c.from_user.id)
    await c.answer("❌ Оплата отменена", cache_time=5)
    await c.message.edit_text(text=await generate_user_text_profile(user),
                              reply_markup=ikb.main_menu_keyboard(user))
    
    logger.fatal(f"Пользователь [{c.from_user.id}] отменил оплату счета")


@callback_router.callback_query(F.data.startswith("download_product@"))
async def download_product(c: CallbackQuery):
    product_id = int(c.data.split("@")[1])
    file_path = f'downloads/{product_id}.rar'  # Укажите путь к вашему файлу
    await c.message.answer_document(caption="Приятного использования",
                                    document=FSInputFile(path=file_path))
    
@callback_router.callback_query(F.data == "user_ref_exchange_time")
async def user_ref_exchange_time(c: CallbackQuery):
    user = await requests_user.get_user_by_telegram_id(c.from_user.id)
    if user.balance <= 1.0:
        await c.answer("\t\tНедостаточно средств\n\nМинимальная сумма для перевода: 1.0 $",
                       show_alert=True)
        return
    
    await c.message.edit_text(text=f"Вы действительно хотите перевести <strong>{user.balance} $</strong> в <strong>{int(user.balance) * 4}</strong> часов подписки?\n\nВыберите продукт, чтобы получить часы подписки",
                              reply_markup=await ikb.exchange_balance_to_product_time())
    
@callback_router.callback_query(F.data.startswith("user_accept_exchange_balance@"))
async def user_accept_exchange_balance(c: CallbackQuery):
    product_id = int(c.data.split("@")[1])
    user = await requests_user.get_user_by_telegram_id(c.from_user.id)
    bal = int(user.balance)

    status = await requests_sub.add_subscription_hours_to_user(bal * 4, c.from_user.id, product_id)
    if not status:
        await c.answer("❌ Произошла неизвестная ошибка. Попробуйте позже")
        return
    user.balance = user.balance - bal
    await requests_user.update_user(user)
    await c.message.edit_text(text=f"✅ Вы успешно перевели <strong>{bal} $</strong> с вашего реферального баланса в <strong>{bal * 4}</strong> часов подписки!",
                              reply_markup=ikb.back_to_main_menu_keyboard())
    
    logger.fatal(f"Пользователь [{c.from_user.id}] перевел [{bal} $] с реферального баланса в [{bal * 4}] часов подписки для [{product_id}]")

# ---------------------------------------------------
# ---------------------------------------------------

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
        logger.fatal(f"Пользователь [{c.from_user.id}] отправил запрос на вывод [{user.balance} $] с баланса")


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
        ► <strong>В данном разделе вы можете получить информацию о ваших рефералах, прибыли от них и получить свою реферальную ссылку для заработка денег</strong>
        ► <strong>Для особо активных пользователей процент от пополнений увеличивается</strong>
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
        text += f"\n    ► <i>#{promocode.name}</i> - <b>{product.name}</b> на <code>{promocode.product_duration / 3600}</code><b> час(ов)</b>"

    return text


async def generate_product_menu_text() -> str:
    return """► [ 💠 Товары ]
        ➖➖➖➖➖➖➖➖➖➖    
        B данном разделе вы можете приобрести или продлить подписку для различных продуктов
    """


async def generate_current_product_menu_text(product: Product) -> str:
    text = f"""► [ 🔑 Меню товара ]
        ➖➖➖➖➖➖➖➖➖➖    
        Название: <code>{product.name}</code>
        Описание: {product.description}
        Версия: <code>{product.version}</code>
        ➖➖➖➖➖➖➖➖➖➖    
            """
    text += """
► [ 📩 Информация ]
        ➖➖➖➖➖➖➖➖➖➖
        ► <strong>При нажатии на кнопки ниже автоматически будет создан счет в <i>Crypto Bot</i></strong> 
        ► <strong>Чтобы приобрести продукт оплатите счет</strong>               
    """

    return text


async def generate_buy_subscription_text() -> str:
    return "Для того, чтобы купить данный продукт оплатите счет в <i>CryptoBot</i>\n " \
           "У вас есть 5 минут на оплату, после чего счет <strong>перестанет существовать</strong> и при попытке его " \
           "пополнить вы потеряете деньги и не получите ничего\n\n<strong>Рекомендуем</strong> указывать свой <i>Telegram ID</i> в коментарии к платежу"


async def generate_subscriptions_menu_text(telegram_id: int) -> str:
    text = "► [ 🔑 Подписки ]\n\t➖➖➖➖➖➖➖➖➖➖"

    subs = await requests_sub.get_user_subscriptions(telegram_id)
    count = 0
    for sub in subs:
        count += 1
        product = await requests_product.get_product_by_id(sub.product_id)
        text += f"""
► [ 🔑 {product.name} ]
    ► Статус > Активна
    ► Дата покупки > <code>{await timestamp_to_sub_end_date(sub.start_date)}</code>
    ► Дата окончания > <code>{await timestamp_to_sub_end_date(sub.end_date)}</code>
    ➖➖➖➖➖➖➖➖➖➖
                    """

    if count < 1:
        text += f"""
        ► <i><b>У вас нет активных подписок 😕</b></i>
        """
        return text

    return text


async def generate_product_info_menu_text(product: Product) -> str:
    text = f"► [ 🔑 {product.name} ]\n\t➖➖➖➖➖➖➖➖➖➖\n\n"

    text += product.description

    return text


async def timestamp_to_sub_end_date(timestamp: int) -> str:
    current_datetime = datetime.datetime.fromtimestamp(timestamp)
    return current_datetime.strftime('%d-%m-%Y | %H:%M:%S')


# ================================================================
# =====================ADMIN======================================
# ================================================================


@callback_router.callback_query(F.data.startswith("admin_"))
async def admin_callback(c: CallbackQuery):
    logger.fatal(f"Пользователь [{c.from_user.id}] воспользовался админ функцией [{c.data}]")
    user = await requests_user.get_user_by_telegram_id(c.from_user.id)

    if not user.isAdmin:
        await c.answer("❌ Нет доступа", show_alert=True)
        return

    callback_name = c.data.split("admin_")[1]

    match callback_name:
        case "apanel_menu":
            await apanel_menu(c)
        case "refsystem_menu":
            await admin_refsytem_menu(c)
        case "product_menu":
            await admin_product_menu(c)
        case "promocode_menu":
            await admin_promocode_menu(c)
        case "manage_users":
            await admin_manage_users(c)
        case "logs":
            await admin_download_logs(c)
        case _ if callback_name.startswith("edit_product_menu@"):
            product_id = int(callback_name.split("@")[1])
            await admin_edit_product_menu(c, product_id)
        case _ if callback_name.startswith("admin_edit_product:"):
            edit_type = str(callback_name.split(":")[1]).split("@")[0]
            product_id = str(callback_name.split(":")[1]).split("@")[1]

            await admin_edit_product(c, edit_type, product_id)
        case _ if callback_name.startswith("logs_download@"):
            type = callback_name.split("@")[1]
            await admin_download_logs_get(c, type)
        case _:
            await c.answer(text="❌ Недопустимый параметр", show_alert=True)


async def apanel_menu(c: CallbackQuery) -> None:
    await c.message.edit_text(text="Админ панель",
                              reply_markup=ikb.apanel_menu_keyboard())


async def admin_refsytem_menu(c: CallbackQuery) -> None:
    await c.message.edit_text(text=await generate_admin_refsystem_menu_text(),
                              reply_markup=ikb.admin_refsystem_menu_keyboard())


async def admin_product_menu(c: CallbackQuery) -> None:
    products = await requests_product.get_all_products()
    await c.message.edit_text(text="Меню продуктов",
                              reply_markup=ikb.admin_product_menu_keyboard(products))


async def admin_edit_product_menu(c: CallbackQuery, product_id: int) -> None:
    product = await requests_product.get_product_by_id(product_id)

    await c.message.edit_text(text=await generate_admin_edit_product_menu_text(product),
                              reply_markup=ikb.admin_edit_product_menu_keyboard(product))


async def admin_edit_product(c: CallbackQuery, edit_type: str, product_id: str) -> None:
    # TODO: добавить проверку на то, что такой параметр и реализацию для него
    match edit_type:
        case "name":
            pass
        case "description":
            pass
        case "manual":
            pass
        case "version":
            pass
        case "subs":
            pass
        case "state":
            pass
        case _:
            await c.answer(text="❌ Недопустимый параметр", show_alert=True)


async def admin_promocode_menu(c: CallbackQuery) -> None:
    await c.message.edit_text(text="Промокоды", reply_markup=ikb.admin_promocode_menu_keyboard())

async def admin_manage_users(c: CallbackQuery) -> None:
    await c.message.edit_text(text="Управление пользователями",
                              reply_markup=await ikb.admin_manage_users_keyboard())

async def admin_download_logs(c: CallbackQuery) -> None:
    await c.message.edit_text(text="При выборе <strong>Последний</strong> будет загружен лог файл текущего процесса бота\n\n"\
                                   "При выборе <strong>Все логи</strong> будут выгружены все доступные логи",
                                   
                                   reply_markup=ikb.download_logs_keyboard())
    
async def admin_download_logs_get(c: CallbackQuery, type: str) -> None:
    if type == "latest":
        file_path = f'logs/latest.log'
        await c.message.answer_document(caption="Последний лог файл текущего процесса бота",
                                    document=FSInputFile(path=file_path))
    else:
        await c.answer("Создается архив со всеми логами. Ожидайте")
        source_folder = 'logs/old'
        archive_name = f'logs/download_{int(time.time())}'
        shutil.make_archive(archive_name, 'zip', source_folder)
        await c.message.answer_document(caption="Все логи успешно выгружены",
                                    document=FSInputFile(path=f"{archive_name}.zip"))
    



@callback_router.callback_query(F.data.startswith("create_promocode_apanel?"))
async def create_promocode_apanel(c: CallbackQuery, state: FSMContext):
    creation_code = c.data.split("?")[1]

    product_id = creation_code.split("&")[0]
    promo_name = creation_code.split("&")[1]
    promo_uses = creation_code.split("&")[2]
    promo_duration = creation_code.split("&")[3]
    promo_end = creation_code.split("&")[4]

    try:
        result = await requests_promocode.add_promocode(promo_name, promo_uses, promo_end, product_id, promo_duration)
        await state.clear()
        if not result:
            await c.message.edit_text(text="Произошла неизвестная ошибка при создании промокода. Промокод не создан",
                                      reply_markup=ikb.back_to_main_menu_keyboard())
        else:
            await c.message.edit_text(
                text=f"Промокод с названием #{promo_name} успешно создан! Осталось активаций: <strong>{promo_uses}</strong>",
                reply_markup=ikb.back_to_main_menu_keyboard())
            logger.fatal(f"Администратор [{c.from_user.id}] создал промокод с названием [{promo_name}]")
    except Exception as e:
        await c.message.edit_text(text=f"Произошла внутренняя ошибка: \n\n\n{e}",
                                  reply_markup=ikb.back_to_main_menu_keyboard())
        
    
@callback_router.callback_query(F.data == "withdraw_requests_menu")
async def withdraw_requests_menu(c: CallbackQuery):
    await c.message.edit_text(text="Заявки на вывод средств от пользователей",
                              reply_markup=await ikb.withdraw_requests_menu_keyboard())
    
@callback_router.callback_query(F.data.startswith("withdraw_request@"))
async def withdraw_request(c: CallbackQuery):
    request_id = int(c.data.split("@")[1])
    
    request = await requests_user.get_withdraw_by_id(request_id)
    user = await requests_user.get_user_by_telegram_id(request.telegram_id)

    await c.message.edit_text(text=f"Заявка на вывод от @{user.username}\n\n",
                              reply_markup=ikb.withdraw_request_keyboard(request.telegram_id))


@callback_router.callback_query(F.data.startswith("user_withdraw_request_"))
async def user_withdraw_request(c: CallbackQuery):
    type = str(c.data.split("user_withdraw_request_")[1]).split("@")[0]
    user_id = str(c.data.split("user_withdraw_request_")[1]).split("@")[1]
    user = await requests_user.get_user_by_telegram_id(user_id)
    withdraw_request = await requests_user.get_withdraw_by_telegram_id(user_id)

    match type:
        case "balance_history":
            historyText = f"История баланса пользователя {user_id}\n\n"
            counter = 1
            user_paid_invoices = await requests_user.get_paid_invoices_by_telegram_id(user_id)
            for invoice in user_paid_invoices:  
                historyText += f"💵 <code>[{counter}]</code> > <strong>[{invoice.telegram_id}]</strong> оплатил <i>#IV{invoice.get_invoice_info()[0][1]}</i> на <code>{invoice.get_invoice_info()[3][1]}$</code>\n"
                counter += 1
            
            for referal_id in user.get_referals():
                referral = await requests_user.get_paid_invoices_by_telegram_id(referal_id)
                for invoice in referral:
                    historyText += f"🎭 <code>[{counter}]</code> > <strong>[{invoice.telegram_id}]</strong> оплатил <i>#IV{invoice.get_invoice_info()[0][1]}</i> на <code>{invoice.get_invoice_info()[3][1]}$</code>\n"
                    counter += 1

            await c.message.edit_text(text=historyText, reply_markup=ikb.back_to_witdraw_request_keyboard(withdraw_request.id))
        case "accept":
            await requests_user.accept_withdraw_request(user_id)
            await c.answer(text="✅ Заявка на вывод средств одобрена")
            await c.message.edit_text(text="Заявки на вывод средств от пользователей",
                              reply_markup=await ikb.withdraw_requests_menu_keyboard())
            await c.bot.send_message(chat_id=user_id, text="✅ Ваша заявка на вывод средств одобрена!")
            logger.fatal(f"Администратор [{c.from_user.id}] одобрил заявку на вывод средств от пользователя [{user_id}]")
        case "decline":
            await requests_user.decline_withdraw_request(user_id)
            await c.answer(text="❌ Заявка на вывод средств отклонена")
            await c.message.edit_text(text="Заявки на вывод средств от пользователей",
                              reply_markup=await ikb.withdraw_requests_menu_keyboard())
            await c.bot.send_message(chat_id=user_id, text="❌ Ваша заявка на вывод средств отклонена!")
            logger.fatal(f"Администратор [{c.from_user.id}] отклонил заявку на вывод средств от пользователя [{user_id}]")
        case _:
            await c.answer(text="❌ Недопустимый параметр", show_alert=True)



# ================================================================

async def generate_admin_edit_product_menu_text(product: Product) -> str:
    text = f"► [ 🔑 {product.name} ]\n\t"
    return text


async def generate_admin_refsystem_menu_text() -> str:
    text = "Реф. система\n\n\tТекущий общий процент: <code>10%</code>"
    return text

# ================================================================
