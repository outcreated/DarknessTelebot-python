from aiogram.types import InlineKeyboardMarkup
from data.telebot_manager import KeyboardBuilder
from database.database_core import Product, SubscriptionPattern, User
from database import requests_sub, requests_product, requests_user


def back_to_main_menu_keyboard() -> InlineKeyboardMarkup:
    builder = KeyboardBuilder()
    builder.btn(text="⬅️ В главное меню", callback_data="main_menu")
    return builder.build(sizes=(1,))


def check_preregister_subscribed() -> InlineKeyboardMarkup:
    builder = KeyboardBuilder()
    builder.btn(text="♻️ Проверить подписку", callback_data="check_preregister_subscribed")
    return builder.build(sizes=(1,))


def main_menu_keyboard(user: User) -> InlineKeyboardMarkup:
    builder = KeyboardBuilder()
    # 🎭🎁📩💠⚙️🔒🔰
    builder.btn(text="🎭 Реф. Система", callback_data="user_refsystem_menu")
    builder.btn(text="🎁 Промокоды", callback_data="user_promocode_menu")
    builder.btn(text="🔑 Подписки", callback_data="user_subscriptions_menu")
    builder.btn(text="💠 Товары", callback_data="user_product_menu")
    # builder.btn(text="⚙️ Настройки", callback_data="user_settings_menu")
    if user.isAdmin:
        builder.btn(text="🔒 Админ-панель", callback_data="admin_apanel_menu")
    builder.btn(text="🔰 Помощь", callback_data="open_darkness_manager", url="https://t.me/darknessmanager")
    if user.isAdmin:
        return builder.build(sizes=(2, 2, 1, 1))
    else:
        return builder.build(sizes=(2, 2, 1))


def referal_menu_keyboard() -> InlineKeyboardMarkup:
    builder = KeyboardBuilder()
    builder.btn(text="⏱ Перевести в часы", callback_data="user_ref_exchange_time")
    builder.btn(text="💸 Вывести деньги", callback_data="user_ref_withdraw_money")
    builder.btn(text="⬅️ Назад", callback_data="main_menu")

    return builder.build(sizes=(2, 1))


def promocode_menu_keyboard() -> InlineKeyboardMarkup:
    builder = KeyboardBuilder()
    builder.btn(text="❤️‍🔥 Активировать промокод", callback_data="user_activate_promocode")
    builder.btn(text="⬅️ Назад", callback_data="main_menu")

    return builder.build(sizes=(1, 1))


def activated_promocode_menu_keyboard() -> InlineKeyboardMarkup:
    builder = KeyboardBuilder()
    builder.btn(text="⬅️ Вернуться в меню", callback_data="main_menu")

    return builder.build(sizes=(1,))


def product_menu_keyboard(products: tuple[Product]) -> InlineKeyboardMarkup:
    builder = KeyboardBuilder()

    for product in products:
        builder.btn(text=product.name, callback_data=f"user_product_menu@{product.id}")

    builder.keyboard.adjust(3, True)

    builder.btn(text="⬅️ Вернуться в меню", callback_data="main_menu")

    return builder.build()


def current_product_menu_keyboard(subscriptions: tuple[SubscriptionPattern]) -> InlineKeyboardMarkup:
    builder = KeyboardBuilder()

    for subscription in subscriptions:
        builder.btn(text=f"💸 {subscription.cost} $ | {int(subscription.duration / 86400)} дн.",
                    callback_data=f"user_buy_subscription@{subscription.id}")

    builder.keyboard.adjust(3, True)

    builder.btn(text="⬅️ Назад", callback_data="user_product_menu")

    return builder.build()


def crypto_bot_pay_keyboard(url: str) -> InlineKeyboardMarkup:
    builder = KeyboardBuilder()
    builder.btn(text="💸 Оплатить", callback_data="-", url=url)
    builder.btn(text="🚫 Отмена", callback_data="user_cancel_buy_subscription")
    builder.btn(text="♻️ Обновить статус платежа", callback_data="update_invoice_status")

    return builder.build(sizes=(2, 1))


def settings_menu_keyboard() -> InlineKeyboardMarkup:
    builder = KeyboardBuilder()
    builder.btn(text=f"✅ Новые рефералы", callback_data="setting_new_ref")
    builder.btn(text=f"✅ Покупка реферала", callback_data="setting_ref_buy")
    builder.btn(text=f"✅ Оповещения от администрации", callback_data="setting_admin_alerts")
    builder.btn(text=f"✅ Напоминания о подписках", callback_data="setting_subscriptions")
    builder.btn(text="⬅️ Назад", callback_data="main_menu")
    builder.btn(text="🚫 Выключить все", callback_data="setting_off_all")

    return builder.build(sizes=(1, 1, 1, 1, 2))


async def subscriptions_menu_keyboard(telegram_id: int) -> InlineKeyboardMarkup:
    builder = KeyboardBuilder()

    subscriptions = await requests_sub.get_user_subscriptions(telegram_id=telegram_id)

    for subscription in subscriptions:
        product = await requests_product.get_product_by_id(subscription.product_id)
        builder.btn(f"{product.name}", f"user_info_product@{product.id}")
        builder.keyboard.adjust(3, True)

    builder.btn(text="⬅️ Назад", callback_data="main_menu")

    return builder.build()


async def generate_product_info_menu_keyboard(product: Product) -> InlineKeyboardMarkup:
    builder = KeyboardBuilder()

    builder.btn(text="📚 Мануал", callback_data=f"*", url=product.manual_url)
    builder.btn(text="🧩 Скачать", callback_data=f"download_product@{product.id}")
    builder.btn(text="⬅️ Назад", callback_data="main_menu")

    return builder.build(sizes=(2, 1))


def apanel_menu_keyboard() -> InlineKeyboardMarkup:
    builder = KeyboardBuilder()
    builder.btn(text=f"🎭 Реф. система", callback_data="admin_refsystem_menu")
    builder.btn(text=f"💠 Товары", callback_data="admin_product_menu")

    builder.btn(text=f"🎁 Промокоды", callback_data="admin_promocode_menu")
    builder.btn(text=f"🤖 Бот", callback_data="admin_")

    builder.btn(text=f"📝 Скачать логи", callback_data="admin_")
    builder.btn(text=f"🔔 Отправить рассылку", callback_data="admin_")

    builder.btn(text=f"🧩 Управление пользователями", callback_data="admin_manage_users")

    builder.btn(text="⬅️ Назад", callback_data="main_menu")

    return builder.build(sizes=(2, 2, 2, 1, 1))


def admin_refsystem_menu_keyboard() -> InlineKeyboardMarkup:
    builder = KeyboardBuilder()

    builder.btn(text="Изменить общий процент", callback_data="*")
    builder.btn(text="⬅️ Назад", callback_data="admin_apanel_menu")

    return builder.build(sizes=(1, 1))


def admin_product_menu_keyboard(products: tuple[Product]) -> InlineKeyboardMarkup:
    builder = KeyboardBuilder()
    for product in products:
        builder.btn(text=product.name, callback_data=f"admin_edit_product_menu@{product.id}")

    builder.keyboard.adjust(3, True)

    builder.btn(text="⬅️ Назад", callback_data="admin_apanel_menu")
    return builder.build()


def admin_edit_product_menu_keyboard(product: Product) -> InlineKeyboardMarkup:
    builder = KeyboardBuilder()

    builder.btn(text="Название", callback_data=f"admin_edit_product:name@{product.id}")
    builder.btn(text="Описание", callback_data=f"admin_edit_product:description@{product.id}")
    builder.btn(text="Версия", callback_data=f"admin_edit_product:version@{product.id}")
    builder.btn(text="Мануал", callback_data=f"admin_edit_product:manual@{product.id}")
    builder.btn(text="Варианты подписок", callback_data=f"admin_edit_product:subs@{product.id}")
    builder.btn(text="Состояние", callback_data=f"admin_edit_product:state@{product.id}")

    builder.btn(text="⬅️ Назад", callback_data="admin_product_menu")

    return builder.build(sizes=(2, 2, 1, 1, 1))


def admin_promocode_menu_keyboard() -> InlineKeyboardMarkup:
    builder = KeyboardBuilder()

    builder.btn(text="⚙️ Создать промокод", callback_data="a_create_promocode")
    builder.btn(text="⬅️ Назад", callback_data="admin_apanel_menu")

    return builder.build(sizes=(1, 1))


async def create_promocode_product_selection_keyboard(promo_name: str, promo_uses: str, promo_duration: str,
                                                      promo_end: str) -> InlineKeyboardMarkup:
    builder = KeyboardBuilder()

    products = await requests_product.get_all_products()

    for product in products:
        builder.btn(text=product.name,
                    callback_data=f"create_promocode_apanel?{product.id}&{promo_name}&{promo_uses}&{promo_duration}&{promo_end}")

    builder.keyboard.adjust(3, True)
    return builder.build()

async def exchange_balance_to_product_time():
    builder = KeyboardBuilder()
    products = await requests_product.get_all_products()
    for product in products:
        builder.btn(text=product.name, callback_data=f"user_accept_exchange_balance@{product.id}")

    builder.keyboard.adjust(3, True)

    builder.btn(text="❌ Отмена", callback_data="main_menu")

    return builder.build()

async def admin_manage_users_keyboard():
    builder = KeyboardBuilder()
    withdraw_requests = await requests_user.get_all_withdraws()
    users = await requests_user.get_all_users()

    usersCount = 0
    withdraw_requestsCount = 0
    for user in users:
        usersCount += 1
    for withdraw_request in withdraw_requests:
        withdraw_requestsCount += 1

    builder.btn(text=f"🔎 Найти пользователя [{usersCount}]", callback_data="search_user_by_id")
    builder.btn(text=f"💸 Заявки на вывод [{withdraw_requestsCount}]", callback_data="withdraw_requests_menu")
    builder.btn(text="⬅️ Назад", callback_data="admin_apanel_menu")

    return builder.build(sizes=(1, 1, 1))

def manage_user_keyboard(telegram_id: int) -> InlineKeyboardMarkup:
    builder = KeyboardBuilder()
    builder.btn(text="Сбросить подписки", callback_data=f"manageuser_clear_subscriptions@{telegram_id}")
    builder.btn(text="Обнулить баланс", callback_data=f"manageuser_clear_balance@{telegram_id}")
    builder.btn(text="⬅️ Назад", callback_data="admin_apanel_menu")

    return builder.build(sizes=(2, 1))

async def withdraw_requests_menu_keyboard() -> InlineKeyboardMarkup:
    builder = KeyboardBuilder()
    withdraw_requests = await requests_user.get_all_withdraws()

    for withdraw_request in withdraw_requests:
        user = await requests_user.get_user_by_telegram_id(withdraw_request.telegram_id)

        builder.btn(text=f"{user.username} | {withdraw_request.amount} $", 
                    callback_data=f"withdraw_request@{withdraw_request.id}")
        
    builder.keyboard.adjust(2, True)
    builder.btn(text="⬅️ Назад", callback_data="admin_apanel_menu")
    return builder.build()

def withdraw_request_keyboard(telegram_id) -> InlineKeyboardMarkup:
    builder = KeyboardBuilder()

    builder.btn(text="💾 История баланса", callback_data=f"user_withdraw_request_balance_history@{telegram_id}")
    builder.btn(text="✅ Одобрить заявку", callback_data=f"user_withdraw_request_accept@{telegram_id}")
    builder.btn(text="❌ Отклонить заявку", callback_data=f"user_withdraw_request_decline@{telegram_id}")
    builder.btn(text="⬅️ Назад", callback_data="withdraw_requests_menu")

    return builder.build(sizes=(1, 2, 1))

def back_to_witdraw_request_keyboard(request_id: int) -> InlineKeyboardMarkup:
    builder = KeyboardBuilder()
    builder.btn(text="⬅️ Назад", callback_data=f"withdraw_request@{request_id}")

    return builder.build()





