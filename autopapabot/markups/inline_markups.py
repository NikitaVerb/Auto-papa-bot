from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from autopapabot.filters.callback_factories import CarMakeCallbackFactory
import sqlite3 as sq


def get_catalog_kb(car_makes, index, back=True, forward=True) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for car_make in car_makes[index]:
        builder.button(text=car_make, callback_data=CarMakeCallbackFactory(car_make=car_make))
    builder.adjust(2)

    if forward and back:
        builder.row(InlineKeyboardButton(text='⬅️ НАЗАД️', callback_data='catalog_move_back'),
                    InlineKeyboardButton(text='ЕЩЁ ➡', callback_data='catalog_move_forward'))

    elif back:
        builder.row(InlineKeyboardButton(text='⬅️ НАЗАД️', callback_data='catalog_move_back'))
    elif forward:
        builder.row(InlineKeyboardButton(text='ЕЩЁ ➡', callback_data='catalog_move_forward'))

    kb = builder.as_markup()
    return kb


def get_inline_main_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='каталог'))
    kb = builder.as_markup()
    return kb


def get_move_kb(now_index, all_index, forward=True, back=True):
    builder = InlineKeyboardBuilder()

    if back: builder.button(text='⬅️', callback_data='move_back')
    if any((back, forward)): builder.button(text=f'{now_index + 1}/{all_index} моделей', callback_data='pass')
    if forward: builder.button(text='➡', callback_data='move_forward')

    builder.button(text='Узнать подробнее', url='https://t.me/otdel_prodazh_autopapa')
    if back and forward:
        builder.adjust(3)
    else:
        builder.adjust(2)
    kb = builder.as_markup()
    return kb
