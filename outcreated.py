import os
from typing import Optional
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
from tools import get_logger_timestamp


def log(logmsg, telegram_id):
    file_path = f"logs/users/{telegram_id}.csv"

    if not os.path.exists(file_path):
        with open(file_path, 'w') as file:
            file.write(f"{get_logger_timestamp()}({telegram_id}) > {logmsg}\n")
    else:
        with open(file_path, 'a') as file:
            file.write(f"{get_logger_timestamp()}({telegram_id}) > {logmsg}\n")


class Keyboard:
    def __init__(self):
        self.keyboard = InlineKeyboardBuilder()
        self.buttons = []

    def btn(self, text, callback_data, url: Optional[str] = "_"):
        if url == "_":
            button = InlineKeyboardButton(text=text,
                                          callback_data=callback_data)
        else:
            button = InlineKeyboardButton(text=text,
                                          callback_data=callback_data,
                                          url=url)
        self.buttons.append(button)
        return self

    def build(self,
              sizes: Optional[tuple[int]] = (2,),
              repeat: Optional[bool] = False):
        for button in self.buttons:
            self.keyboard.add(button)

        return self.keyboard.adjust(*sizes, repeat=repeat).as_markup()
