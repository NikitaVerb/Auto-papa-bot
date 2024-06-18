from aiogram import Router, F
from aiogram.filters import Command
from autopapabot.markups.reply_markups import get_admin_main_kb
from aiogram import types
from autopapabot.filters import user_rights
import autopapabot.google_sheets as gs
from aiogram.filters.command import CommandObject
import sqlite3 as sq

router = Router()
router.message.filter(user_rights.UserRightFilter())


@router.message(Command('start'))
async def cmd_start(message: types.Message):
    await message.answer(f'Вы вошли с правами администратора', reply_markup=get_admin_main_kb())
    await message.answer(f'Добро пожаловать в бот-каталог диллера <b>AUTO PAPA</b>. Чтобы открыть или обновить каталог'
                         f' нажмите на кнопку «Каталог»👇🏻')

@router.message(Command('setadmin'))
async def cmd_setadmin(message: types.Message,
                       command: CommandObject):
    admin_id = command.args
    if admin_id is None:
        await message.answer(
            "Ошибка: не определены аргументы"
        )
        return

    try:
        admin_id = int(admin_id)
    except ValueError:
        await message.answer(
            "Ошибка: неправильный формат команды. Пример:\n"
            "/setadmin 123456789"
        )
        return

    with sq.connect('cars.db') as con:
        con.row_factory = sq.Row
        cursor = con.cursor()
        cursor.execute(f'INSERT INTO admins_id (id) VALUES ({admin_id})')

    await message.answer('id администратора добавлен')




@router.message(F.text == 'Обновить каталог')
async def update_catalog(message: types.Message):
    msg1 = await message.answer('Каталог обновляется...')
    text = gs.update_catalog()
    await msg1.delete()
    await message.answer(text)



@router.message(F.photo)
async def send_photo_id(message: types.Message):
    await message.answer(message.photo[-1].file_id)

