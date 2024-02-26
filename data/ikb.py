from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup
from aiogram.types import WebAppInfo
from data.telebot_manager import KeyboardBuilder
from database.database_core import User

def check_preregister_subscribed() -> InlineKeyboardMarkup:
    builder = KeyboardBuilder()
    builder.btn(text="♻️ Проверить подписку", callback_data="check_preregister_subscribed")
    return builder.build(sizes=(1,))

def main_menu_keyboard(user: User) -> InlineKeyboardMarkup:
    builder = KeyboardBuilder()
    # 🎭🎁📩💠⚙️🔒🔰
    builder.btn(text="🎭 Реф. Система", callback_data="user_refsystem_menu")
    builder.btn(text="🎁 Промокоды", callback_data="1")
    builder.btn(text="📩 Информация", callback_data="1")
    builder.btn(text="💠 Товары", callback_data="1")
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