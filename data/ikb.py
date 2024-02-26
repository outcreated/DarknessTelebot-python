from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup
from aiogram.types import WebAppInfo
from data.telebot_manager import KeyboardBuilder

def ikbWebAppTest() -> InlineKeyboardMarkup:
    builder = KeyboardBuilder()

    builder.btn("Test 1")
    builder.btn("Test 2")
    builder.btn("Test 3")
    builder.btn("Test 4")
    builder.btn("Test 5")
    builder.btn("Test 6")

    return builder.build(sizes=(2, 2, 1, 1))