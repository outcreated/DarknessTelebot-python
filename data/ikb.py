from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup
from aiogram.types import WebAppInfo
from data.telebot_manager import KeyboardBuilder
from database.database_core import Product, SubscriptionPattern, User

def check_preregister_subscribed() -> InlineKeyboardMarkup:
    builder = KeyboardBuilder()
    builder.btn(text="♻️ Проверить подписку", callback_data="check_preregister_subscribed")
    return builder.build(sizes=(1,))

def main_menu_keyboard(user: User) -> InlineKeyboardMarkup:
    builder = KeyboardBuilder()
    # 🎭🎁📩💠⚙️🔒🔰
    builder.btn(text="🎭 Реф. Система", callback_data="user_refsystem_menu")
    builder.btn(text="🎁 Промокоды", callback_data="user_promocode_menu")
    builder.btn(text="📩 Информация", callback_data="1")
    builder.btn(text="💠 Товары", callback_data="user_product_menu")
    builder.btn(text="⚙️ Настройки", callback_data="1")
    if user.isAdmin:
        builder.btn(text="🔒 Админ-панель", callback_data="1")
    builder.btn(text="🔰 Помощь", callback_data="1")
    if user.isAdmin:
        return builder.build(sizes=(2, 2, 1, 1, 1))
    else:
        return builder.build(sizes=(2, 2, 1, 1))
    
def referal_menu_keyboard() -> InlineKeyboardMarkup:
    builder = KeyboardBuilder()
    builder.btn(text="💸 Вывести деньги", callback_data="user_ref_withdraw_money")
    builder.btn(text="⬅️ Назад", callback_data="main_menu")

    return builder.build(sizes=(1, 1))

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
        builder.btn(text=f"💸 {subscription.cost} $ | {int(subscription.duration/86400)} дн.", 
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
