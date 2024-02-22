from aiogram import Router, types, F
from aiogram.filters import Command, Filter
from tools import check_user_register
from database.requests import get_user_by_telegram_id, get_product_by_id
from keyboards.inline import generate_user_menu, generate_user_product_menu, generate_user_check_product_menu, get_buy_product_kb
from database import requests
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import market

user_router = Router()


class RegisterProtect(Filter):
    async def __call__(self, message: types.Message):
        if await check_user_register(message.from_user.id):
            return True
        else:
            await message.answer("Вы не зарегистрированы в системе!\n\n"
                                 "Чтобы использовать функционал бота пройдите "
                                 "регистрацию")
            return False


class UserUsePromocode(StatesGroup):
    promo_name = State()


@user_router.callback_query(F.data == "open_product_menu")
async def open_user_product_menu(call: types.CallbackQuery):
    await call.message.edit_caption(
        caption="Тут вы можете купить"
        " различные товары от нас или "
        "продлить подписку на них",
        reply_markup=await generate_user_product_menu())


@user_router.callback_query(F.data.startswith("user_check_product_"))
async def user_check_product(call: types.CallbackQuery):
    product_id = call.data.split("_check_product_")[1]

    product = await requests.get_product_by_id(int(product_id))
    await call.message.edit_caption(caption=f"{product.product_name}",
                                    reply_markup=await generate_user_check_product_menu(product_id, call.from_user.id))


@user_router.callback_query(F.data.startswith("user_update_invoice_status:"))
async def update_invoice_status(call: types.CallbackQuery):
    status = await market.update_invoice(call.from_user.id)
    product_id = call.data.split(":")[1]
    product_duration = call.data.split("-")[1]

    if status == "active":
        await call.answer("❌ Счет не оплачен")
    elif status == "paid":
        await call.answer("✅ Оплата прошла успешно!")
        await requests.give_user_product(call.from_user.id, product_id, product_duration)
        await requests.add_referer_balance(call.from_user.id)
        await call.message.delete()


@user_router.callback_query(F.data.startswith("user_create_invoice_product_"))
async def user_buy_product(call: types.CallbackQuery):
    print(call.data)
    rawdata = call.data.split("_product_")[1]
    product_id = rawdata.split(":")[0]
    duration = rawdata.split(":")[1]

    await call.message.answer("Для того, чтобы купить данный продукт оплатите счет в CryptoBot\n\nУ вас есть "
                              "5 минут на оплату, после чего счет перестанет существовать и при попытке его "
                              "пополнить вы потеряете деньги и не получите ничего\n\nРекомендуем указывать свой telegram id в коментарии к платежу", reply_markup=await get_buy_product_kb(product_id, duration, call.from_user.id))


@user_router.callback_query(F.data == "open_promo_menu")
async def open_user_promo_menu(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("Введите промокод, который хотите активировать")
    await state.set_state(UserUsePromocode.promo_name)


@user_router.callback_query(F.data.startswith("download_"))
async def user_download_file(call: types.CallbackQuery):
    file_path = call.data.split("_")[1]
    file_path = f'files/{file_path}.rar'  # Укажите путь к вашему файлу
    await call.message.answer_document(document=types.FSInputFile(path=file_path))


@user_router.message(UserUsePromocode.promo_name)
async def user_used_promo(message: types.Message, state: FSMContext):
    res = await requests.update_promocode(message.text, message.from_user.id)

    if res == "promo_used":
        await message.answer("Вы уже использовали данный промокод!")
    elif res == "promo_not_exist":
        await message.answer("Данного промокода не существует или его срок действия истек")
    else:

        await message.answer(f"Промокод <strong>{message.text}</strong> успешно"
                             f" использован\nВам выдан продукт: {res}")
    await state.clear()


@user_router.callback_query(F.data == "open_user_profile")
async def open_user_profile(call: types.CallbackQuery):
    await call.message.edit_caption(caption=await get_user_profile(
        call.from_user.id),
        reply_markup=await generate_user_menu())


@user_router.message(Command("menu"), RegisterProtect())
async def message(message: types.Message):
    file_path = "images/user_profile.jpg"
    await message.answer_photo(photo=types.FSInputFile(path=file_path),
                               caption=await get_user_profile(
                                   message.from_user.id),
                               reply_markup=await generate_user_menu())


@user_router.message(Command("promo"), RegisterProtect())
async def use_promo(message: types.Message):
    promo_name = message.text.split(" ")[1]
    response = await requests.update_promocode(promo_name, message.from_user.id)

    if response == "promo_used":
        await message.answer("Вы уже использовали данный промокод!")
    elif response == "promo_not_exist":
        await message.answer("Данного промокода не существует или его срок действия истек")
    else:
        await message.answer(f"Промокод <strong>{promo_name}</strong> успешно"
                             f" использован\nВам выдан продукт: {response}")


async def get_user_profile(telegram_id: int) -> str:
    user = await get_user_by_telegram_id(telegram_id)
    profile = f"""
    > [ 🪪 Ваш профиль ]
    ► 🔰 ID: <code>{user.telegram_id}</code>
    ► 📆 Регистрация: <code>{user.register_date.split()[0]}</code>
    ► 🧩 Рефералов: {len(user.referals.split(" ")) - 1}
    ► 💰 Реф. баланс: {user.referal_balance} $
    ► 📎 Реф. Ссылка <code>https://t.me/darknessparser_bot?start=ref-{telegram_id}</code>
    """
    if len(user.current_products) == 0:
        no_product = "\n🙁 У вас нет купленных подписок\n"
        profile = profile + no_product
    else:
        user = await requests.get_user_by_telegram_id(telegram_id=telegram_id)
        products = user.current_products
        product_id = products.split(":")[0]
        product = await requests.get_product_by_id(int(product_id))
        product_left = products.split(":")[1]

        product_text = f"""\n>  [ 🔐 {product.product_name} ]
            ► 🔑 Подписка  [ Активна ]
            ► ⏳ Осталось: [ {product_left} ч ]
            """
        profile = profile + product_text

    '''
    >  [ 🔐 Подписка ]
        ► 🔑 Статус  [ Активна ]
        ► ⏳ Осталось: [ 240 ч ]
    '''
    return profile
