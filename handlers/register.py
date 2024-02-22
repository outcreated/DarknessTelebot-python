import config

from aiogram.filters import Command
from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv, find_dotenv

from keyboards.inline import subscribe_channel_button
from tools import check_user_register
from database.requests import set_users
from database import requests

register_router = Router()
load_dotenv(find_dotenv())
# StateFilter(None),


@register_router.message(Command("start"))
async def cmd_food(message: types.Message, state: FSMContext):
    if not await check_user_register(message.from_user.id):
        referer_id = 0
        if not await is_subscribed(message.from_user.id, message.bot):
            file_path = "images/not_subscribed.jpg"
            await message.answer_photo(
                photo=types.FSInputFile(path=file_path),
                caption="\nЧтобы использовать бота"
                " <b>подпишитесь на канал</b>\n",
                reply_markup=await subscribe_channel_button()
            )
            return
        if 'ref' in message.text:
            if (len(message.text.split(" ")) > 1 and
                    len(str(message.text.split(" ")[1]).split("-")) > 1):
                referer_id = str(message.text.split(" ")[1]).split("-")[1]
                if await check_user_register(int(referer_id)):
                    await requests.update_user_referals(
                        message.from_user.id, int(referer_id))
                    await message.answer(
                        text=f"Вы успешно зарегистрировались в системе рефералом: "
                        f"{referer_id}"
                    )
                else:
                    await message.answer(
                        text="Вы успешно зарегистрировались в системе\n\n"
                        "Используйте команду /menu"
                    )
        else:
            await message.answer(
                text="Вы успешно зарегистрировались в системе\n\n"
                "Чтобы открыть меню используйте команду /menu"
            )

        user = message.from_user
        await set_users(user.id, user.username, 0, "", "", referer_id, "")
    else:
        await message.answer(text="Вы уже зарегистрированы \n"
                             "Повторная регистрация невозможна")

    # ебарим состояние к юзеру
    # await state.set_state(state=Registered())


async def is_subscribed(user_id: int, bot) -> bool:
    chat_member = await bot.get_chat_member(
        chat_id=f"@{config.SUBSCRIBE_CHANNEL_NAME}",
        user_id=user_id)
    return chat_member.status in ['member', 'creator']
