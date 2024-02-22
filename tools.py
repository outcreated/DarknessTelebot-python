import time
from colorama import Fore
from database.requests import get_users


def cis(string):
    """
    Обычный print() с автоматическим добавлением текущего time-stamp

    :param string: Строка, перед которой будет установлен time-stamp
    """
    print(time.strftime(
        f'{Fore.RESET}['
        f'{Fore.LIGHTYELLOW_EX}%H{Fore.RESET}:'
        f'{Fore.LIGHTYELLOW_EX}%M{Fore.RESET}:'
        f'{Fore.LIGHTYELLOW_EX}%S{Fore.RESET}] ') + string + Fore.RESET)


def get_log_time():
    return time.strftime(
        f'{Fore.RESET}['
        f'{Fore.LIGHTYELLOW_EX}%H{Fore.RESET}:'
        f'{Fore.LIGHTYELLOW_EX}%M{Fore.RESET}:'
        f'{Fore.LIGHTYELLOW_EX}%S{Fore.RESET}] ')


def get_logger_timestamp():
    return time.strftime('[%H:%M:%S] ')


async def check_user_register(user_telegram_id: int) -> bool:
    """
    Проверка пользователя на наличие в базе данных

    user_telegram_id: Telegram ID пользователя, которого необходимо
    проверить на наличие в базе данных
    """
    users = await get_users()

    for user in users:
        if user.telegram_id == user_telegram_id:
            return True

    return False
