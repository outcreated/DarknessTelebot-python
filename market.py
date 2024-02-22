import os
import time
import config

from aiocryptopay import AioCryptoPay, Networks
from aiogram.client.session import aiohttp
from aiocryptopay.models.update import Update
from colorama import Fore
from aiocryptopay.models.invoice import Invoice

invoices_list = {}


crypto = AioCryptoPay(config.CRYPTO_BOT_TOKEN, network=Networks.MAIN_NET)


@crypto.pay_handler()
async def invoice_paid(update: Update, app) -> None:
    print(update)


async def create_invoice(cost: str, telegram_id: int):
    fiat_invoice = await crypto.create_invoice(amount=int(cost), fiat='USD', currency_type='fiat')
    invoices_list[f"{telegram_id}"] = fiat_invoice.invoice_id
    return fiat_invoice.bot_invoice_url


async def update_invoice(telegram_id):
    old_invoice = await crypto.get_invoices(invoice_ids=invoices_list[str(telegram_id)])
    for index, value in enumerate(old_invoice):
        if index == 1:
            return value[1]


async def init():
    me = await crypto.get_me()
    print(
        f"Бот успешно подключился к {Fore.LIGHTMAGENTA_EX}CryptoBot {Fore.RESET}| Номер приложения: {Fore.LIGHTCYAN_EX}{me.app_id} {Fore.RESET}| Имя: {Fore.LIGHTCYAN_EX}{me.name} {Fore.RESET}| Сеть: {Fore.LIGHTCYAN_EX}{me.payment_processing_bot_username}")
