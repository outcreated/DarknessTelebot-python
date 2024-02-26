import config
import oc
import datetime
from data import ikb
from aiogram import Router, Bot, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from database import requests_user
from database.database_core import User

command_router = Router()
preRegisterUsers = {}


@command_router.message(Command("menu"))
async def main_menu_handler(m: Message) -> None:
    user = await requests_user.get_user_by_telegram_id(m.from_user.id)
    await m.answer(text=await generate_user_text_profile(user), reply_markup=ikb.main_menu_keyboard(user))

@command_router.message(CommandStart())
async def commandStartExecutor(m: Message) -> None:
    referrer_id = -1

    try:
        referrer_id = int(m.text.split("-")[1])
    except IndexError as e:
        pass

    preRegisterUsers[m.from_user.id] = referrer_id

    status = await check_user_channel_subscribed(m.from_user.id, m.bot)
    if not status:
        await m.answer(text="Чтобы использовать нашего бота, подпишитесь на канал, чтобы быть вкурсе всех новостей <a href='https://t.me/darknessparser'>ᅠ ᅠ </a>",
                       reply_markup=ikb.check_preregister_subscribed())
        return
    status = await requests_user.add_user(m.from_user.id, m.from_user.username, referrer_id)
    preRegisterUsers.pop(m.from_user.id)
    if status:
        await m.answer("Вы успешно зарегистрировались! Чтобы открыть главное меню бота, напишите /menu")
    else:
        await m.answer("Вы уже зарегистрирваны!")


async def check_user_channel_subscribed(user_id: int, bot: Bot) -> bool:
    chat_member = await bot.get_chat_member(
        chat_id=f"@{config.SUBSCRIBE_CHANNEL_NAME}",
        user_id=user_id)
    return chat_member.status in ['member', 'creator', 'administrator']

async def generate_user_text_profile(user: User) -> str:
    profile =  f"""
    ► [ 🪪 Главное меню ]
    ➖➖➖➖➖➖➖➖➖➖
    ► [ 🔰 ] ID > <code>{user.telegram_id}</code>
    ► [ 📝 ] Регистрация > <code>{await timestamp_to_date(user.register_date)}</code>
    ► [ 🧩 ] Рефералов > <code>{len(user.get_referals())}</code>
    ► [ 💰 ] Реф. баланс > <code>{user.balance} $</code>
    ➖➖➖➖➖➖➖➖➖➖
    """

    return profile

async def timestamp_to_date(timestamp: int) -> str:
    current_datetime = datetime.datetime.fromtimestamp(timestamp)
    return current_datetime.strftime('%d-%m-%Y')
    
