import oc
import config

from aiocryptopay import AioCryptoPay, Networks
from aiogram.client.session import aiohttp
from aiocryptopay.models.update import Update
from colorama import Fore
from aiocryptopay.models.invoice import Invoice
from database import requests_server

invoices_list = {}


crypto = AioCryptoPay(config.CRYPTO_BOT_TOKEN, network=Networks.TEST_NET)


@crypto.pay_handler()
async def invoice_paid(update: Update, app) -> None:
    print(update)


async def create_invoice(cost: str, telegram_id: int, subscription_id: int):
    fiat_invoice = await crypto.create_invoice(amount=cost, fiat='USD', currency_type='fiat')
    invoices_list[telegram_id] = [fiat_invoice.invoice_id, subscription_id]
    #invoices_list[f"{telegram_id}"] = fiat_invoice.invoice_id
    return fiat_invoice.bot_invoice_url


async def update_invoice(telegram_id) -> tuple[str, int]:
    old_invoice = await crypto.get_invoices(invoice_ids=invoices_list[telegram_id][0])
    invoice_info = []

    for index, value in enumerate(old_invoice):
        if index in [0,1,2,4,6]:
            invoice_info.append(value)
    for index, value in enumerate(old_invoice):
        if index == 1:
            if value[1] == "paid":
                await requests_server.save_paid_invoice(telegram_id, invoice_info)
            return (value[1], invoices_list[telegram_id][1])

async def delete_invoice(telegram_id) -> None:
    del invoices_list[telegram_id]


async def init():
    me = await crypto.get_me()
    oc.log("info", f"Бот успешно подключился к {Fore.LIGHTMAGENTA_EX}CryptoBot {Fore.RESET}| Имя приложения: {Fore.LIGHTCYAN_EX}{me.name} {Fore.RESET}")