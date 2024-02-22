from keyboards import admin_keyboards
from keyboards import inline

from aiogram import F, Bot, Router, types
from aiogram.filters import Command, Filter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import requests
from outcreated import log


admin_router = Router()
globalmessage_temp = types.Message


class AddProduct(StatesGroup):
    name = State()
    description = State()
    messages_to_delete = []


class Alert(StatesGroup):
    message = State()
    confirm = State()


class EditProduct(StatesGroup):
    value = State()
    editType = ""


class AdminProtect(Filter):
    async def __call__(self, message: types.Message):
        return message.from_user.id in [6171432104, 1890015035, 6695376459]


@admin_router.message(AdminProtect(), Command("apanel"))
async def apanel(message: types.Message):
    log("Адмнинистратор вошел в админ-панель", message.from_user.id)
    # file_path = "images/admin_panel.jpg"
    await message.answer(
        text="Добро пожаловать в панель администратора",
        reply_markup=await admin_keyboards.get_admin_panel_kb())


@admin_router.message(AdminProtect(), Command("alert"))
async def message(message: types.Message, state: FSMContext):
    log("Администратор начал создавать оповещение", message.from_user.id)
    await state.set_state(Alert.message)
    await message.answer("Отправьте сообщение, которое вы хотите разослать"
                         " всем пользователям")


@admin_router.message(AdminProtect(), Command("crb"))
async def clear_referal_balance(message: types.Message):
    tg_id = message.text.split(" ")[1]
    await requests.clear_referer_balance(tg_id)
    await message.answer("Реферальный баланс пользователя обнулен")


@admin_router.message(AdminProtect(), Command("refbal"))
async def check_referal_balance(message: types.Message):
    tg_id = message.text.split(" ")[1]
    refbal = await requests.check_referer_balance(tg_id)
    await message.answer(f"Реферальный баланс пользователя: {refbal}")


@admin_router.message(AdminProtect(), Command("makepromo"))
async def make_promo_command(message: types.Message):
    # /makepromo promo 5 5 1:2
    # name useleft timeleft givecode
    promo_name = message.text.split(" ")[1]
    use_left = message.text.split(" ")[2]
    time_left = message.text.split(" ")[3]
    give_code = message.text.split(" ")[4]

    await requests.add_promocode_to_database(promo_name,
                                             use_left,
                                             time_left,
                                             give_code)
    await message.answer(f"Промокод: <strong>{promo_name}</strong> добавлен в базу данных!")
    log(f"Администратор создал промокод '{promo_name}'", message.from_user.id)


@admin_router.message(AdminProtect(), Alert.message)
async def alert_message(message: types.Message, state: FSMContext):
    await state.set_state(Alert.confirm)
    global globalmessage_temp
    globalmessage_temp = message
    await message.send_copy(chat_id=message.from_user.id)
    await message.answer("Вы действительно хотите отправить это сообщение?",
                         reply_markup=await inline.alert_confirm())


@admin_router.message(AdminProtect(), EditProduct.value)
@admin_router.message(AdminProtect(), AddProduct.name)
async def set_product_name(message: types.Message, state: FSMContext):

    await state.update_data(name=message.text)
    await state.set_state(AddProduct.description)
    await message.answer(text="Введите описание продукта",
                         reply_markup=await admin_keyboards.
                         get_addproduct_menu(False))


@admin_router.message(AdminProtect(), AddProduct.description)
async def set_product_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await requests.set_temp_product_description(message.text)
    data = await state.get_data()
    await message.answer(
        text=f"Вы действительно хотите добавить данный продукт?\n\n"
        f"<blockquote>Название: <b><i>{data['name']}</i></b>\n"
        f"Описание: <b><i>{data['description']}</i></b></blockquote>",
        reply_markup=await admin_keyboards.
        get_addproduct_menu(True, data['name']))
    await state.clear()


@admin_router.callback_query(F.data == "admin_send_alert")
async def message_inline(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(Alert.message)
    await call.message.answer("Отправьте сообщение, которое вы хотите разослать"
                              " всем пользователям")


@admin_router.callback_query(F.data == "admin_addproduct_cancel")
async def admin_addproduct_cancel(call: types.CallbackQuery,
                                  state: FSMContext):
    await state.clear()
    await requests.clear_temp_product_description()
    caption = "Добро пожаловать в меню редактирования товаров"
    await call.message.edit_text(text=caption,
                                 inline_message_id=call.
                                 inline_message_id,
                                 reply_markup=await admin_keyboards.
                                 get_admin_product_menu())


@admin_router.callback_query(F.data == "admin_addproduct_menu")
async def add_product_to_product_menu(call: types.CallbackQuery,
                                      state: FSMContext):
    await state.set_state(AddProduct.name)
    await call.message.answer(text="Введите имя нового продукта",
                              reply_markup=await admin_keyboards.
                              get_addproduct_menu())


@admin_router.callback_query(F.data.startswith("$add_product"))
async def create_product(call: types.CallbackQuery):
    name = call.data.split(":")[1]
    await requests.set_product(name,
                               await requests.get_temp_product_description())
    await requests.clear_temp_product_description()
    caption = "Добро пожаловать в меню редактирования товаров"
    await call.message.edit_text(text=caption,
                                 inline_message_id=call.
                                 inline_message_id,
                                 reply_markup=await admin_keyboards.
                                 get_admin_product_menu())
    await call.answer("✅ Продукт успешно добавлен")
    log(f"Администратор создал продукт '{name}'", call.from_user.id)
    #


@admin_router.callback_query(F.data.startswith("admin_manageproduct_"))
async def manage_product(call: types.CallbackQuery):
    print(call.data)
    product_id = call.data.split("_manageproduct_")[1]
    product = await requests.get_product_by_id(product_id=product_id)

    caption = str(f"Меню управления продуктом: <b><code>{product.product_name}</code></b>\n\n"
                  f"Описание: <b><blockquote>{product.product_description}</blockquote></b>"
                  f"Фото: <b>{product.product_photo}</b>\n"
                  f"Состояние: <b>{product.product_active}</b>\n"
                  f"Ключ продукта: <code>{product.product_key}</code>")
    await call.message.edit_text(text=caption,
                                 reply_markup=await admin_keyboards.
                                 get_edit_product_menu(product_id))


@admin_router.callback_query(F.data.startswith("admin_edit_product_"))
async def edit_product(call: types.CallbackQuery):
    edit_type = call.data.split("_edit_product_")[1].split("_")[0]
    edit_product_id = call.data.split("_edit_product_")[1].split("_")[1]

    print(edit_type + " > " + edit_product_id)


@admin_router.callback_query(F.data == "admin_send_alert_confirm")
async def send_alert_confirm(call: types.CallbackQuery, state: FSMContext):
    global globalmessage_temp
    await call.message.answer("Подождите. Происходит рассылка сообщений. "
                              "При большом количестве пользователей это может "
                              "занять много времени")
    counter = 0
    for user in await requests.get_users():
        try:
            await globalmessage_temp.send_copy(chat_id=user.telegram_id)
            counter = + 1
        except Exception:
            pass
    await call.message.answer(f"Рассылка успешно завершена! Всего "
                              f"пользователей получили сообщение: <b>{counter}</b>")
    await state.clear()
    log("Администратор отправил оповещение всем пользователям", call.from_user.id)


@admin_router.callback_query(F.data == "admin_send_alert_cancel")
async def send_alert_cancel(call: types.CallbackQuery, state: FSMContext):
    await state.clear()


@admin_router.callback_query()
async def admin_callback_query(call: types.CallbackQuery):
    # await message.answer_photo(photo=types.FSInputFile(path=file_path),
    #                            caption="Добро пожаловать в панель администратора",
    #                            reply_markup=await admin_keyboards.get_admin_panel_kb())

    match call.data:
        case "admin_panel_menu":
            caption = "Добро пожаловать в панель администратора"
            await call.message.edit_text(text=caption,
                                         inline_message_id=call.
                                         inline_message_id,
                                         reply_markup=await admin_keyboards.
                                         get_admin_panel_kb())
            log("Администратор вошел в админ-панель", call.from_user.id)
        case "admin_product_menu":
            caption = "Добро пожаловать в меню редактирования товаров"
            await call.message.edit_text(text=caption,
                                         inline_message_id=call.
                                         inline_message_id,
                                         reply_markup=await admin_keyboards.
                                         get_admin_product_menu())
            log("Администратор вошел меню редактирования продуктов", call.from_user.id)
        case _:
            pass
