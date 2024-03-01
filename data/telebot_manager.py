import inspect
from typing import Optional

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


class KeyboardBuilder:
    def __init__(self):
        self.keyboard = InlineKeyboardBuilder()
        self.buttons = []

    def btn(self, text, callback_data: Optional[str] = "_", url: Optional[str] = "_"):
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
              sizes: Optional[tuple[int]] = (3,),
              repeat: Optional[bool] = False):
        for button in self.buttons:
            self.keyboard.add(button)
        return self.keyboard.adjust(*sizes, repeat=repeat).as_markup()
