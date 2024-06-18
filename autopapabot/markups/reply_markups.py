from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_main_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text='Каталог')
    kb.button(text='Связаться')
    kb.button(text='Наш телеграм-канал🚘')
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)


def get_admin_main_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text='Каталог')
    kb.button(text='Связаться')
    kb.button(text='Обновить каталог')
    kb.button(text='Наш телеграм-канал🚘')
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)
