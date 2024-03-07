import time
import os

from colorama import Fore as fr


def get_timestamp() -> str:
    return time.strftime(f"[{fr.LIGHTMAGENTA_EX}%H:%M:%S{fr.RESET}] ", time.localtime())


def log(level: str, message: str) -> None:
    if level == "info":
        print(get_timestamp() + f"[{fr.CYAN}INFO{fr.RESET}] {message}")
    elif level == "warn":
        print(get_timestamp() + f"[{fr.YELLOW}WARNING{fr.RESET}] {message}")
    elif level == "err":
        print(get_timestamp() + f"[{fr.RED}ERROR{fr.RESET}] {message}")


def cls():
    os.system('cls' if os.name == 'nt' else 'clear')
