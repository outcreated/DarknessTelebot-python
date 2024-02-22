import threading
from typing import Optional
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup
from database.requests import get_products
from database import requests
from database.models import Product
import market

from outcreated import Keyboard
import config


async def subscribe_channel_button() -> InlineKeyboardMarkup:
    return Keyboard().btn("🔔 Подписаться",
                          "subscribe_button",
                          f"https://t.me/{config.SUBSCRIBE_CHANNEL_NAME}").build()


async def alert_confirm() -> InlineKeyboardMarkup:
    br = Keyboard()
    br.btn("✅ Отправить", "admin_send_alert_confirm")
    br.btn("❌ Отменить", "admin_send_alert_cancel")

    return br.build()


async def generate_admin_panel_kb() -> InlineKeyboardMarkup:
    br = Keyboard()
    br.btn("🔰 Продукты", "admin_product_menu")
    br.btn("🎁 Промокоды", "admin_promo_menu")
    br.btn("🎭 Реф. Система", "admin_refsystem_menu")
    br.btn("🪪 Пользователи", "admin_users_menu")
    br.btn("🔔 Отправить рассылку", "admin_send_alert")

    return br.build(sizes=(2, 2, 1))


async def generate_admin_product_menu():
    products = await get_products()
    br = Keyboard()
    for product in products:
        br.btn(product.product_name,
               f"admin_manageproduct_{product.product_id}")
    br.keyboard.adjust(4, True)
    br.btn("⚙️ Добавить продукт", "admin_addproduct_menu")
    br.btn("⬅️ Назад", "admin_panel_menu")
    return br.build()


async def generate_user_product_menu():
    products = await get_products()

    br = Keyboard()
    for product in products:
        if product.product_active:
            br.btn(product.product_name,
                   f"user_check_product_{product.product_id}")
    br.keyboard.adjust(3, repeat=True)
    br.btn("⬅️ Назад", "open_user_profile")
    return br.build()


async def generate_user_check_product_menu(prod_id: int, telegram_id: int):
    br = Keyboard()
    product_variant = await requests.get_product_variant_by_product_id(prod_id)
    product = await requests.get_product_by_id(prod_id)
    user = await requests.get_user_by_telegram_id(telegram_id)

    br.btn(f"{product_variant.product_payment_cost} $ / {product_variant.product_payment_duration} часа",
           f"user_create_invoice_product_{prod_id}:{product_variant.product_payment_cost}")
    if len(user.current_products) > 0:
        if int(user.current_products.split(":")[0]) > 0:
            br.btn("🧩 Скачать", f"download_{product.product_key}")
    br.btn("⬅️ Назад", "open_product_menu")
    return br.build(sizes=(1, 2))


async def get_buy_product_kb(product_id, duration, telegram_id):
    br = Keyboard()
    invoice_url = await market.create_invoice(duration, telegram_id)
    br.btn("Оплатить счет", "click_buy_product_btn", str(invoice_url))
    br.btn("Обновить статус платежа",
           f"user_update_invoice_status:{product_id}-{duration}")
    return br.build(sizes=(1, 1))


async def generate_addproduct_menu(boolean: Optional[bool] = False,
                                   product_name: Optional[str] = "",
                                   product_description: Optional[str] = ""):
    br = Keyboard()

    if boolean:
        br.btn("✅ Добавить", f"$add_product:{product_name}")
    br.btn("❌ Отменить", "admin_addproduct_cancel")

    return br.build(sizes=(1, 1))


async def generate_user_menu() -> InlineKeyboardMarkup:
    br = Keyboard()

    br.btn("🎭 Рефералы", "open_referal_menu")
    br.btn("🎁 Промокод", "open_promo_menu")
    br.btn("💭 Информация", "open_info_menu")
    br.btn("💠 Товары", "open_product_menu")
    br.btn("🔰 Помощь", "open_admin_chat", "t.me/darknessmanager")

    return br.build(sizes=(2, 2, 1))


async def generate_edit_product_menu(product_id: int) -> InlineKeyboardMarkup:
    product = await requests.get_product_by_id(product_id=product_id)

    br = Keyboard()
    br.btn("Изменить имя", f"admin_edit_product_name_{product_id}")
    br.btn("Изменить описание",
           f"admin_edit_product_description_{product_id}")
    br.btn("Изменить фото", f"admin_edit_product_photo_{product_id}")
    br.btn("Изменить файл", f"admin_edit_product_file_{product_id}")
    br.btn("Изменить подписки", f"admin_edit_product_variants_{product_id}")
    br.btn(f"Состояние {await get_product_activate(product=product)}",
           f"admin_edit_product_active_{product_id}")
    br.btn("⬅️ Назад", "admin_product_menu")

    return br.build(sizes=(2, 2, 1, 1, 1))


async def get_product_activate(product: Product) -> str:
    if product.product_active:
        return "✅"
    else:
        return "❌"
