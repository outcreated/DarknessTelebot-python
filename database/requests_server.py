from sqlalchemy.ext.asyncio import async_session
from database.database_core import PaidInvoice, async_session


async def save_paid_invoice(telegram_id: int, invoice_info):
    async with async_session() as s:
        invoice = PaidInvoice(telegram_id=telegram_id)
        invoice.set_invoice_info(invoice_info)
        s.add(invoice)
        await s.commit()
