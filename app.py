import telebot, asyncio, logging, sys, threading, oc, platform, os

from colorama import Fore as fr
from colorama import init as colorama_init
from server import authorization_service

colorama_init()


def init() -> None:
    oc.cls()
    authorization_service.init_auth_server()
    logging.basicConfig(level=logging.INFO,
                        stream=sys.stdout,
                        format=oc.get_timestamp() +
                               f'[{fr.CYAN}%(levelname)s{fr.RESET}] %(message)s')

    asyncio.run(telebot.startBot())


def install_dependencies():
    system = platform.system()
    if system == 'Windows':
        command = 'py -m pip install -r requirements.txt'
    else:
        command = 'python3 -m pip install -r requirements.txt'

    # Устанавливаем зависимости из requirements.txt
    os.system(command)


if __name__ == '__main__':
    # install_dependencies()
    init()
