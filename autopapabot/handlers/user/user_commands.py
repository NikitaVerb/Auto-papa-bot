from aiogram import Router, F, Bot
from aiogram.filters import Command
from autopapabot.markups.reply_markups import get_main_kb
from autopapabot.markups.inline_markups import get_catalog_kb, get_move_kb
from autopapabot.filters.callback_factories import CarMakeCallbackFactory
from aiogram import types
from aiogram.types.input_media_photo import InputMediaPhoto
import sqlite3 as sq
from datetime import datetime

router = Router()
router.message.filter()


@router.message(Command('start'))
async def cmd_start(message: types.Message):
    await message.answer(f'Добро пожаловать в бот-каталог диллера <b>AUTO PAPA</b>. Чтобы открыть или обновить каталог'
                         f' нажмите на кнопку «Каталог»👇🏻', reply_markup=get_main_kb())


@router.message(F.text == 'Каталог')
async def send_catalog(message: types.Message, dct: dict):
    photo_id = 'AgACAgIAAxkBAAMOZW8t4vhV9nUnIANPWvA6ExlMdTgAAjnxMRswl3lLLWziQdFKsG0BAAMCAAN4AAMzBA'

    if message.from_user.id not in dct:
        dct[message.from_user.id] = {}

    if 'msg' in dct[message.from_user.id]:
        del dct[message.from_user.id]['msg']

    with sq.connect('cars.db') as con:
        con.row_factory = sq.Row
        cursor = con.cursor()
        cursor.execute("""SELECT DISTINCT car_make FROM cars""")

        car_makes = []
        piece_car_makes = []
        cnt = 0
        for res in cursor:
            if cnt < 6:
                piece_car_makes.append(res['car_make'])
                cnt += 1
            else:
                car_makes.append(piece_car_makes)
                piece_car_makes = [res['car_make']]
                cnt = 1
        car_makes.append(piece_car_makes)

    dct[message.from_user.id] |= {'car_makes': car_makes, 'car_makes_index': 0}

    forward = dct[message.from_user.id]['car_makes_index'] != len(dct[message.from_user.id]['car_makes']) - 1
    msg = await message.answer_photo(photo=photo_id,
                                     caption='<b>Выберите марку авто:</b> ',
                                     reply_markup=get_catalog_kb(car_makes=car_makes,
                                                                 index=0,
                                                                 back=False,
                                                                 forward=forward))

    await message.delete()


@router.callback_query(F.data.startswith('catalog_move_'))
async def catalog_after_press(callback: types.CallbackQuery, dct: dict, bot: Bot):
    media = 'AgACAgIAAxkBAAMOZW8t4vhV9nUnIANPWvA6ExlMdTgAAjnxMRswl3lLLWziQdFKsG0BAAMCAAN4AAMzBA'
    match callback.data.split('_')[-1]:
        case 'forward':
            if dct[callback.from_user.id]['car_makes_index'] + 1 != len(dct[callback.from_user.id]['car_makes']):
                dct[callback.from_user.id]['car_makes_index'] += 1

        case 'back':
            if dct[callback.from_user.id]['car_makes_index'] != 0:
                dct[callback.from_user.id]['car_makes_index'] -= 1

    forward = dct[callback.from_user.id]['car_makes_index'] != len(dct[callback.from_user.id]['car_makes']) - 1
    back = (dct[callback.from_user.id]['car_makes_index'] != 0)
    car_makes = dct[callback.from_user.id]['car_makes']
    index = dct[callback.from_user.id]['car_makes_index']

    text = '<b>Выберите марку авто:</b> '

    await bot.edit_message_media(chat_id=callback.message.chat.id,
                                 message_id=callback.message.message_id,
                                 media=InputMediaPhoto(media=media, caption=text),
                                 reply_markup=get_catalog_kb(car_makes, index, forward=forward, back=back))


@router.message(F.text == 'Связаться')
async def send_contact(message: types.Message, dct: dict):
    await message.answer("<a href='https://t.me/otdel_prodazh_autopapa'>https://t.me/otdel_prodazh_autopapa</a>")
    await message.delete()


@router.message(F.text == 'Наш телеграм-канал🚘')
async def send_tg_contact(message: types.Message, dct: dict):
    await message.answer("<a href='https://t.me/avto_papa_rus'>https://t.me/avto_papa_rus</a>")
    await message.delete()


@router.callback_query(CarMakeCallbackFactory.filter())
async def send_car_cart(callback: types.CallbackQuery,
                        callback_data: CarMakeCallbackFactory,
                        dct: dict,
                        bot: Bot):
    with sq.connect('cars.db') as con:
        con.row_factory = sq.Row
        cursor = con.cursor()
        cursor.execute(
            f'''
            SELECT * FROM cars
            WHERE car_make={repr(callback_data.car_make)}
            ''')
    await callback.answer()
    car_info = []
    index = 0
    for info in cursor:
        car_info.append((
            f"<b>Марка:</b> {info['car_make']}\n\n"
            f"<b>Модель:</b> {info['model']}\n\n"
            f"<b>Комплектация:</b> {info['complete_set_of_the_machine']}\n\n"
            f"<b>Цена автомобиля:</b> {format(int(info['price']), ',d').replace(',', ' ')}₽\n\n"
            f"<b>Цена «под ключ»:</b> {format(int(info['price_turnkey']), ',d').replace(',', ' ')}₽\n\n",
            info['photo_id']))

    if callback.from_user.id in dct:
        msg: types.Message = dct[callback.from_user.id].get('msg', None)

        dct[callback.from_user.id] |= {"car_info": car_info, 'index': index}

        text = dct[callback.from_user.id]['car_info'][dct[callback.from_user.id]['index']][0]
        media = dct[callback.from_user.id]['car_info'][dct[callback.from_user.id]['index']][1]

        now_index = dct[callback.from_user.id]['index']
        all_index = len(dct[callback.from_user.id]['car_info'])

        forward = dct[callback.from_user.id]['index'] != len(dct[callback.from_user.id]['car_info']) - 1

        if msg:

            await bot.edit_message_media(chat_id=callback.message.chat.id,
                                         message_id=msg.message_id,
                                         media=InputMediaPhoto(media=media, caption=text),
                                         reply_markup=get_move_kb(now_index=now_index, all_index=all_index,
                                                                  forward=forward, back=False)
                                         )
            dct[callback.from_user.id]['msg'] = msg
        else:





            if forward:
                msg = await callback.message.answer_photo(car_info[0][1], caption=car_info[0][0],
                                                          reply_markup=get_move_kb(now_index=now_index, all_index=all_index,
                                                                                   back=False))
            else:
                msg = await callback.message.answer_photo(car_info[0][1], caption=car_info[0][0],
                                                          reply_markup=get_move_kb(now_index=now_index, all_index=all_index,
                                                                                   back=False, forward=False))

            dct[callback.from_user.id]['msg'] = msg


@router.callback_query(F.data.startswith('move_'))
async def process_after_press(callback: types.CallbackQuery, dct: dict, bot: Bot):
    match callback.data.split('_')[1]:
        case 'forward':
            if dct[callback.from_user.id]['index'] + 1 != len(dct[callback.from_user.id]['car_info']):
                dct[callback.from_user.id]['index'] += 1

        case 'back':
            if dct[callback.from_user.id]['index'] != 0:
                dct[callback.from_user.id]['index'] -= 1

    now_index = dct[callback.from_user.id]['index']
    all_index = len(dct[callback.from_user.id]['car_info'])

    text = dct[callback.from_user.id]['car_info'][dct[callback.from_user.id]['index']][0]
    media = dct[callback.from_user.id]['car_info'][dct[callback.from_user.id]['index']][1]

    forward = dct[callback.from_user.id]['index'] != len(dct[callback.from_user.id]['car_info']) - 1
    back = (dct[callback.from_user.id]['index'] != 0)

    await bot.edit_message_media(chat_id=callback.message.chat.id,
                                 message_id=callback.message.message_id,
                                 media=InputMediaPhoto(media=media, caption=text),
                                 reply_markup=get_move_kb(now_index=now_index, all_index=all_index,
                                                          forward=forward, back=back))


@router.callback_query(F.data == 'pass')
async def pass_callback(callback: types.CallbackQuery):
    await callback.answer()


@router.message(F.text.lower() == 'id')
async def send_id(message: types.Message):
    await message.answer(str(message.from_user.id))
