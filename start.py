# pip freeze > requirements.txt
# установить pip install -r requirements.txt


import logging
import sqlite3
import datetime
import os
import asyncio
import schedule
import time

from config import *

from datetime import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types.input_file import FSInputFile
from aiogram.types import Message

from typing import List, Tuple




# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

   
    
# Создаем базу доступа
con = sqlite3.connect('data/db/role.db')
cur = con.cursor()
cur.execute('''
    CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            us_idtg VARCHAR (20), 
            us_name VARCHAR (40), 
            us_role VARCHAR (10),
            us_region VARCHAR (30),
            us_login VARCHAR (40),
            us_password VARCHAR (40)
            )''')
con.commit()
cur.close()
con.close()

logging.basicConfig(level=logging.INFO, filename='data/logs/log.txt', format='%(asctime)s - %(message)s')
logging.info("🌐 Bot is running")

ITEMS_PER_PAGE = 10


class employees(StatesGroup):
    notes = State()
    msg_id = State()
    region = State()
    new_data = State()
    full_name = State()
    locker_number = State()
    tg_link = State()
    position = State()
    birthday = State()
    hire_date = State()
    phone_main = State()
    phone_backup = State()
    hire_date = State()
    dogovor = State()
    photo = State()
    newpersonphoto = State()
    status = State()
    siz_dress = State()
    siz_shoes = State()

class prof(StatesGroup):
    newadd = State()

class calendar(StatesGroup):
    year = State()
    month = State()
    day = State()

class worktask(StatesGroup):
    addtask = State()
    finish_task = State()
    
    


# Обработчик команды /start
@dp.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    name = message.chat.first_name
    role = user_role(user_id)
    region = user_region(user_id)
    await state.clear()
    if role:
        update_data_role_DB(user_id, name)
        logging.info(f"{name} from {region} press start")
        board = InlineKeyboardBuilder()
        if role == 'admin' or role == 'manager' or role == 'brigadir':
            board.add(types.InlineKeyboardButton(text="Персонал", callback_data="personal"))
        if role == 'admin' or role == 'manager' or role == 'brigadir':
            board.add(types.InlineKeyboardButton(text="Склад", callback_data="warehouse"))
        if role == 'admin' or role == 'manager' or role == 'brigadir':
            board.add(types.InlineKeyboardButton(text="Задания", callback_data="task"))
        board.adjust(1)
        text = check_personal(region)
        sent_message = await message.answer (f"<i>Привет, {name}!!!\nАктивные работники на площадке:</i>\n{text}", parse_mode="HTML", disable_web_page_preview=True, reply_markup=board.as_markup())
        asyncio.create_task(delete_message_after_delay(sent_message.chat.id, sent_message.message_id))
    else:
        sent_message = await message.answer (f"Вы не зарегистрированы", parse_mode="HTML")
        asyncio.create_task(delete_message_after_delay(sent_message.chat.id, sent_message.message_id))


# Общий обработчик нажатий на кнопки
@dp.callback_query()
async def process_callback(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    role = user_role(user_id)
    region = user_region(user_id)
    if role:
        name = callback_query.from_user.first_name
        data = callback_query.data

        if data == "OK":
            await callback_query.answer()
            await state.clear()
            board = InlineKeyboardBuilder()
            if role == 'admin':
                board.add(types.InlineKeyboardButton(text="Персонал", callback_data="personal"))
            if role == 'admin' or role == 'manager':
                board.add(types.InlineKeyboardButton(text="Склад", callback_data="warehouse"))
            if role == 'admin' or role == 'manager' or role == 'brigadir':
                board.add(types.InlineKeyboardButton(text="Задания", callback_data="task"))
            board.adjust(1)
            text = check_personal(region)
            try:
                sent_message = await callback_query.message.edit_text (f"<i>Привет, {name}!!!\nАктивные работники на площадке:</i>\n{text}", parse_mode="HTML", disable_web_page_preview=True, reply_markup=board.as_markup())
                asyncio.create_task(delete_message_after_delay(sent_message.chat.id, sent_message.message_id))
            except Exception as e:
                # Если не получается отредактировать (например, сообщение с фото),
                # удаляем старое и отправляем новое
                await callback_query.message.delete()
                sent_message = await bot.send_message(
                    callback_query.from_user.id,
                    f"<i>Привет, {name}!!!\nАктивные работники на площадке:</i>\n{text}",
                    parse_mode="HTML",
                    disable_web_page_preview=True,
                    reply_markup=board.as_markup()
                )
                asyncio.create_task(delete_message_after_delay(sent_message.chat.id, sent_message.message_id))

        elif data == "role":
            await callback_query.answer()
            await state.clear()
            board = InlineKeyboardBuilder()
            board.add(types.InlineKeyboardButton(text="Ясно", callback_data="OK"))
            sent_message = await callback_query.message.edit_text (f'Ваша роль - {role} из {region}', parse_mode="HTML", disable_web_page_preview=True, reply_markup=board.as_markup())
            asyncio.create_task(delete_message_after_delay(sent_message.chat.id, sent_message.message_id))

        elif data == "personal":
            await callback_query.answer()
            await state.clear()
            with sqlite3.connect(f'data/db/work db/warehouse_{region}.db') as con:
                cur = con.cursor()
                cur.execute('''
                    CREATE TABLE IF NOT EXISTS employees(
                            id INTEGER PRIMARY KEY AUTOINCREMENT, 
                            full_name VARCHAR (100), 
                            fio VARCHAR (100),
                            tg_link VARCHAR (100),
                            position VARCHAR (100), 
                            locker_number VARCHAR (100), 
                            birthday VARCHAR (100), 
                            phone_main VARCHAR (100),  
                            phone_backup VARCHAR (100), 
                            hire_date VARCHAR (100), 
                            dogovor VARCHAR (100), 
                            notes VARCHAR (100), 
                            photo BLOB, 
                            status VARCHAR (100),
                            siz_dress VARCHAR (100),
                            siz_shoes VARCHAR (100),
                            who_add VARCHAR (100)
                            )''')
                cur.execute('''
                    CREATE TABLE IF NOT EXISTS Position(
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            position VARCHAR (100),
                            status VARCHAR (100)
                            )''')
                cur.execute('''
                    CREATE TABLE IF NOT EXISTS logs(
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            who VARCHAR (100),
                            what VARCHAR (100)
                            )''')
                con.commit()
            board = InlineKeyboardBuilder()
            board.add(types.InlineKeyboardButton(text="Активные", callback_data="personal_active"))
            board.add(types.InlineKeyboardButton(text="Уволенные", callback_data="personal_inactive"))
            board.add(types.InlineKeyboardButton(text="Добавить сотрудника", callback_data="personal_add"))
            if role == 'admin' or role == 'manager':
                board.add(types.InlineKeyboardButton(text="Список должностей", callback_data="position_add"))
            board.add(types.InlineKeyboardButton(text="Экспорт в excel", callback_data="personal_export"))
            board.add(types.InlineKeyboardButton(text="↪️Главное меню↩️", callback_data="OK"))
            board.adjust(2, 1, 1, 1)
            sent_message = await callback_query.message.edit_text ('Выбери нужный пункт', parse_mode="HTML", disable_web_page_preview=True, reply_markup=board.as_markup())
            asyncio.create_task(delete_message_after_delay(sent_message.chat.id, sent_message.message_id))
        
        elif data == "position_add":
            await callback_query.answer()
            await state.clear()
            board = InlineKeyboardBuilder()
            if role == 'admin' or role == 'manager':
                board.add(types.InlineKeyboardButton(text="Добавить должность", callback_data="position_new"))
                board.add(types.InlineKeyboardButton(text="Изменить должность", callback_data="position_change"))
                board.adjust (2)
            board.row(types.InlineKeyboardButton(text="↪️Главное меню↩️", callback_data="OK"))
            text = warehouse_position(region)
            sent_message = await callback_query.message.edit_text (f'<b>Существующие должности:</b>\n{text}', parse_mode="HTML", disable_web_page_preview=True, reply_markup=board.as_markup())
            asyncio.create_task(delete_message_after_delay(sent_message.chat.id, sent_message.message_id))
        
        elif data == "position_new":
            await callback_query.answer()
            await state.clear()
            await state.set_state(prof.newadd)
            text = warehouse_position(region)
            board = InlineKeyboardBuilder()
            board.add(types.InlineKeyboardButton(text="↪️Главное меню↩️", callback_data="OK"))
            sent_message = await callback_query.message.edit_text ('<i>Вводи название новой должности</i>', parse_mode="HTML", disable_web_page_preview=True, reply_markup=board.as_markup())
            await state.update_data(msg_id=sent_message.message_id)
            asyncio.create_task(delete_message_after_delay(sent_message.chat.id, sent_message.message_id))

        elif data == "personal_add":
            await callback_query.answer()
            await state.clear()
            await state.set_state(employees.full_name)
            await state.update_data(region=region)
            board = InlineKeyboardBuilder()
            board.add(types.InlineKeyboardButton(text="↪️Главное меню↩️", callback_data="OK"))
            sent_message = await callback_query.message.edit_text ('<b>Добавляем нового сотрудника:</b>\nВводи Фамилию Имя и Отчество полностью\nДля отмены иди в главное меню', parse_mode="HTML", disable_web_page_preview=True, reply_markup=board.as_markup())
            await state.update_data(msg_id=sent_message.message_id)
            asyncio.create_task(delete_message_after_delay(sent_message.chat.id, sent_message.message_id))
        
        elif data == "personal_active":
            await callback_query.answer()
            await state.clear()
            status = 'active'
            await show_employees_page(callback_query, 1, region, status)
        
        elif data == "personal_inactive":
            await callback_query.answer()
            await state.clear()
            status = 'inactive'
            await show_employees_page(callback_query, 1, region, status)

        elif callback_query.data.startswith("page_"):
            await callback_query.answer()
            await state.clear()
            page = int(callback_query.data.split("_")[1])
            status = callback_query.data.split("_")[2]
            await show_employees_page(callback_query, page, region, status)
        
        elif callback_query.data.startswith("employee_"):
            await callback_query.answer()
            user_id = callback_query.from_user.id
            await state.clear()
            await callback_query.message.delete()
            emp_id = callback_query.data.split("_", 1)[1]
            with sqlite3.connect(f'data/db/work db/warehouse_{region}.db') as con:
                cur = con.cursor()
                result = cur.execute('SELECT id, full_name, tg_link, position, locker_number, birthday, phone_main, phone_backup, hire_date, dogovor, notes, photo, siz_dress, siz_shoes, who_add, status FROM employees WHERE id = ?', [emp_id]).fetchone()
                if result:
                    emp_id, full_name, tg_link, position, locker_number, birthday, phone_main, phone_backup, hire_date, dogovor, notes, photo, siz_dress, siz_shoes, who_add, status = result
            birthday_formatted = format_date(birthday)
            hire_date_formatted = format_date(hire_date)
            text = f"<b>ФИО:</b><i> {full_name}</i>\n"
            text += f"<b>Должность:</b><i> {position}</i>\n"
            text += f"<b>Дата рождения:</b><i> {birthday_formatted}</i>\n"
            text += f"<b>Дата трудоустройства:</b><i> {hire_date_formatted}</i>\n"
            text += f"<b>Шкафчик:</b><i> {locker_number}</i>\n"
            text += f"<b>Номер договора:</b><i> {dogovor}</i>\n"
            text += f"<b>Тел основной:</b><i> {phone_main}</i>\n"
            text += f"<b>Тел дополнительный:</b><i> {phone_backup}</i>\n"
            text += f"<b>Телеграмм:</b><i> {tg_link}</i>\n"
            text += f"<b>Размер одежды:</b><i> {siz_dress}</i>\n"
            text += f"<b>Размер обуви:</b><i> {siz_shoes}</i>\n"
            text += f"<b>Добавил:</b><i> {who_add}</i>\n"
            text += f"<b>Заметки:</b><i> {notes}</i>\n"
            if photo:
                try:
                    with open(f'data/temp/image_{user_id}.jpg', 'wb') as file:
                        file.write(photo)
                    scr = FSInputFile(f"data/temp/image_{user_id}.jpg")
                except Exception as e:
                    logging.error(f"Ошибка записи фотки сотрудника в файл: {e}")
                    scr = FSInputFile(f"data/scr/image.png")
            else:
                scr = FSInputFile(f"data/scr/image.png")
            board = InlineKeyboardBuilder()
            board.add(types.InlineKeyboardButton(text="Изменить", callback_data=f"edit:{emp_id}"))
            if status == 'active':
                board.add(types.InlineKeyboardButton(text="Уволить", callback_data=f"inactive:{emp_id}"))
            else:
                board.add(types.InlineKeyboardButton(text="Вернуть", callback_data=f"active:{emp_id}"))
            board.add(types.InlineKeyboardButton(text="↪️Главное меню↩️", callback_data="OK"))
            board.adjust(2, 1)
            sent_message = await bot.send_photo(user_id, photo=scr, caption=text, parse_mode="HTML", reply_markup=board.as_markup())
            asyncio.create_task(delete_message_after_delay(sent_message.chat.id, sent_message.message_id))

        elif callback_query.data.startswith("inactive:"):
            await callback_query.answer()
            user_id = callback_query.from_user.id
            await state.clear()
            await callback_query.message.delete()
            emp_id = callback_query.data.split(":")[1]
            who_logs = who_did(user_id)
            with sqlite3.connect(f'data/db/work db/warehouse_{region}.db') as con:
                cur = con.cursor()
                cur.execute(f'UPDATE employees SET status = ? WHERE id = {emp_id} ', ['inactive'])
                name = (cur.execute('SELECT full_name FROM employees WHERE id = ?', [emp_id]).fetchone())[0]
                cur.execute('INSERT INTO logs (who, what) VALUES (?, ?)', (who_logs, f"Увольнение {name}"))
                con.commit()
            board = InlineKeyboardBuilder()
            board.add(types.InlineKeyboardButton(text="↪️Главное меню↩️", callback_data="OK"))    
            sent_message = await bot.send_message(callback_query.from_user.id, f"<i>{name}\nПереведен в статус <u>неактивных</u> </i>", parse_mode="HTML", disable_web_page_preview=True, reply_markup=board.as_markup())           
            asyncio.create_task(delete_message_after_delay(sent_message.chat.id, sent_message.message_id))

        elif callback_query.data.startswith("active:"):
            await callback_query.answer()
            user_id = callback_query.from_user.id
            await state.clear()
            await callback_query.message.delete()
            emp_id = callback_query.data.split(":")[1]
            who_logs = who_did(user_id)
            with sqlite3.connect(f'data/db/work db/warehouse_{region}.db') as con:
                cur = con.cursor()
                cur.execute(f'UPDATE employees SET status = ? WHERE id = {emp_id} ', ['active'])
                name = (cur.execute('SELECT full_name FROM employees WHERE id = ?', [emp_id]).fetchone())[0]
                cur.execute('INSERT INTO logs (who, what) VALUES (?, ?)', (who_logs, f"Перевод {name} из неактивных в активные"))
                con.commit()
            board = InlineKeyboardBuilder()
            board.add(types.InlineKeyboardButton(text="↪️Главное меню↩️", callback_data="OK"))    
            sent_message = await bot.send_message(callback_query.from_user.id, f"<i>{name}\nПереведен в статус <u>активных</u> </i>", parse_mode="HTML", disable_web_page_preview=True, reply_markup=board.as_markup())           
            asyncio.create_task(delete_message_after_delay(sent_message.chat.id, sent_message.message_id))

        elif callback_query.data.startswith("edit:"):
            await callback_query.answer()
            user_id = callback_query.from_user.id
            await state.clear()
            await callback_query.message.delete()
            emp_id = callback_query.data.split(":", 1)[1]
            with sqlite3.connect(f'data/db/work db/warehouse_{region}.db') as con:
                cur = con.cursor()
                result = cur.execute('SELECT id, full_name, tg_link, position, locker_number, birthday, phone_main, phone_backup, hire_date, dogovor, notes, photo, siz_dress, siz_shoes FROM employees WHERE id = ?', [emp_id]).fetchone()
                if result:
                    emp_id, full_name, tg_link, position, locker_number, birthday, phone_main, phone_backup, hire_date, dogovor, notes, photo, siz_dress, siz_shoes = result
            birthday_formatted = format_date(birthday)
            hire_date_formatted = format_date(hire_date)
            text = "<b>1)</b>Фотография\n"
            text += f"<b>2)</b>ФИО:<i> {full_name}</i>\n"
            text += f"<b>3)</b>Должность:<i> {position}</i>\n"
            text += f"<b>4)</b>Дата рождения:<i> {birthday_formatted}</i>\n"
            text += f"<b>5)</b>Дата трудоустройства:<i> {hire_date_formatted}</i>\n"
            text += f"<b>6)</b>Шкафчик:<i> {locker_number}</i>\n"
            text += f"<b>7)</b>Номер договора:<i> {dogovor}</i>\n"
            text += f"<b>8)</b>Тел основной:<i> {phone_main}</i>\n"
            text += f"<b>9)</b>Тел дополнительный:<i> {phone_backup}</i>\n"
            text += f"<b>10)</b>Телеграмм:<i> {tg_link}</i>\n"
            text += f"<b>11)</b>Размер одежды:<i> {siz_dress}</i>\n"
            text += f"<b>12)</b>Размер обуви:<i> {siz_shoes}</i>\n"
            text += f"<b>13)</b>Заметки:<i> {notes}</i>\n\n<b>Выбери пункт для редактирования</b>"
            if photo:
                try:
                    with open(f'data/temp/image_{user_id}.jpg', 'wb') as file:
                        file.write(photo)
                    scr = FSInputFile(f"data/temp/image_{user_id}.jpg")
                except Exception as e:
                    logging.error(f"Ошибка записи фотки сотрудника в файл: {e}")
                    scr = FSInputFile(f"data/scr/image.png")
            else:
                scr = FSInputFile(f"data/scr/image.png")
            board = InlineKeyboardBuilder()
            board.add(types.InlineKeyboardButton(text="1", callback_data=f"edittable:photo_{emp_id}"))
            board.add(types.InlineKeyboardButton(text="2", callback_data=f"edittable-full_name-{emp_id}"))
            board.add(types.InlineKeyboardButton(text="3", callback_data=f"edittable-position-{emp_id}"))
            board.add(types.InlineKeyboardButton(text="4", callback_data=f"edittable-birthday-{emp_id}"))
            board.add(types.InlineKeyboardButton(text="5", callback_data=f"edittable-hire_date-{emp_id}"))
            board.add(types.InlineKeyboardButton(text="6", callback_data=f"edittable-locker_number-{emp_id}"))
            board.add(types.InlineKeyboardButton(text="7", callback_data=f"edittable-dogovor-{emp_id}"))
            board.add(types.InlineKeyboardButton(text="8", callback_data=f"edittable-phone_main-{emp_id}"))
            board.add(types.InlineKeyboardButton(text="9", callback_data=f"edittable-phone_backup-{emp_id}"))
            board.add(types.InlineKeyboardButton(text="10", callback_data=f"edittable-tg_link-{emp_id}"))
            board.add(types.InlineKeyboardButton(text="11", callback_data=f"edittable-siz_dress-{emp_id}"))
            board.add(types.InlineKeyboardButton(text="12", callback_data=f"edittable-siz_shoes-{emp_id}"))
            board.add(types.InlineKeyboardButton(text="13", callback_data=f"edittable:notes_{emp_id}"))
            board.add(types.InlineKeyboardButton(text="↪️Главное меню↩️", callback_data="OK"))
            board.adjust(6, 6, 1)
            sent_message = await bot.send_photo(user_id, photo=scr, caption=text, parse_mode="HTML", reply_markup=board.as_markup())
            asyncio.create_task(delete_message_after_delay(sent_message.chat.id, sent_message.message_id))

        elif callback_query.data.startswith("edittable:notes_"):
            await callback_query.answer()
            user_id = callback_query.from_user.id
            await state.clear()
            await callback_query.message.delete()
            emp_id = callback_query.data.split("_")[1]
            await state.set_state(employees.notes)
            await state.update_data(user_id=user_id)
            await state.update_data(emp_id=emp_id)
            await state.update_data(region=region)
            board = InlineKeyboardBuilder()
            board.add(types.InlineKeyboardButton(text="↪️Главное меню↩️", callback_data="OK"))
            logging.info(f'{user_id} у {emp_id} правит заметки')
            sent_message = await bot.send_message(callback_query.from_user.id, "<i>Вводи текст, либо иди в главное меню</i>", parse_mode="HTML", disable_web_page_preview=True, reply_markup=board.as_markup())           
            await state.update_data(msg_id=sent_message.message_id)
            asyncio.create_task(delete_message_after_delay(sent_message.chat.id, sent_message.message_id))

        elif callback_query.data.startswith("edittable-"):
            await callback_query.answer()
            user_id = callback_query.from_user.id
            await state.clear()
            await state.set_state(employees.new_data)
            await callback_query.message.delete()
            emp_id = callback_query.data.split("-")[2]
            table = callback_query.data.split("-")[1] 
            await state.update_data(user_id=user_id)
            await state.update_data(emp_id=emp_id)
            await state.update_data(table=table)
            await state.update_data(region=region)
            board = InlineKeyboardBuilder()
            board.add(types.InlineKeyboardButton(text="↪️Главное меню↩️", callback_data="OK"))
            logging.info(f'{user_id} у {emp_id} правит {table}')
            sent_message = await bot.send_message(callback_query.from_user.id, "<i>Вводи новые данные, или иди в главное меню</i>", parse_mode="HTML", disable_web_page_preview=True, reply_markup=board.as_markup())           
            await state.update_data(msg_id=sent_message.message_id)
            asyncio.create_task(delete_message_after_delay(sent_message.chat.id, sent_message.message_id))

        elif callback_query.data.startswith("edittable:photo_"):
            await callback_query.answer()
            user_id = callback_query.from_user.id
            await state.clear()
            emp_id = callback_query.data.split("_")[1]
            await state.set_state(employees.photo)
            await state.update_data(emp_id=emp_id, region=region)
            await callback_query.message.delete()
            board = InlineKeyboardBuilder()
            board.add(types.InlineKeyboardButton(text="↪️Главное меню↩️", callback_data="OK"))
            sent_message = await bot.send_message(callback_query.from_user.id, "<i>Жду новое фото, или иди в главное меню</i>", parse_mode="HTML", disable_web_page_preview=True, reply_markup=board.as_markup())           
            await state.update_data(msg_id=sent_message.message_id)
            asyncio.create_task(delete_message_after_delay(sent_message.chat.id, sent_message.message_id))

        elif callback_query.data.startswith("profession:add_"):
            await callback_query.answer()
            user_id = callback_query.from_user.id
            new_prof = callback_query.data.split("_")[1]
            with sqlite3.connect(f'data/db/work db/warehouse_{region}.db') as con:
                cur = con.cursor()
                cur.execute('INSERT INTO Position (position, status) VALUES (?, ?)', (new_prof, "активна"))
                con.commit()
            text = warehouse_position(region)
            board = InlineKeyboardBuilder()
            if role == 'admin' or role == 'manager':
                board.add(types.InlineKeyboardButton(text="Добавить должность", callback_data="position_new"))
                board.add(types.InlineKeyboardButton(text="Изменить должность", callback_data="position_change"))
                board.adjust (2)
            board.row(types.InlineKeyboardButton(text="↪️Главное меню↩️", callback_data="OK"))
            user_data = await state.get_data()
            msg_id = user_data['msg_id']
            sent_message = await bot.edit_message_text(chat_id=user_id, message_id=msg_id, text=f'<b>Существующие должности:</b>\n{text}', parse_mode="HTML", disable_web_page_preview=True, reply_markup=board.as_markup())           
            await state.update_data(msg_id=sent_message.message_id)
            asyncio.create_task(delete_message_after_delay(sent_message.chat.id, sent_message.message_id))

        elif data == "position_change":
            await callback_query.answer()
            await state.clear()
            user_id = callback_query.from_user.id
            with sqlite3.connect(f'data/db/work db/warehouse_{region}.db') as con:
                cur = con.cursor()
                buttons = cur.execute("SELECT * FROM Position").fetchall()
            board = InlineKeyboardBuilder()
            for button in buttons:
                board.row(types.InlineKeyboardButton(text=f"{button[1]}", callback_data=f"position-change:{button[0]}"))
            board.row(types.InlineKeyboardButton(text="↪️Главное меню↩️", callback_data="OK"))
            sent_message = await callback_query.message.edit_text(f'<b>Выберай, статус какой должности необходимо изменить</b>', parse_mode="HTML", disable_web_page_preview=True, reply_markup=board.as_markup())           
            asyncio.create_task(delete_message_after_delay(sent_message.chat.id, sent_message.message_id))

        elif callback_query.data.startswith("position-change:"):
            await callback_query.answer()
            position_id = callback_query.data.split(":")[1]
            with sqlite3.connect(f'data/db/work db/warehouse_{region}.db') as con:
                cur = con.cursor()
                profession = cur.execute('SELECT position FROM Position WHERE id = ?', [position_id]).fetchone()
            board = InlineKeyboardBuilder()
            board.add(types.InlineKeyboardButton(text="Активировать", callback_data=f"position:activate:{position_id}"))
            board.add(types.InlineKeyboardButton(text="Деактивировать", callback_data=f"position:deactivate:{position_id}"))
            board.adjust(2)
            board.row(types.InlineKeyboardButton(text="↪️Главное меню↩️", callback_data="OK"))
            sent_message = await callback_query.message.edit_text(f'<b>Что необходимо сделать?</b>', parse_mode="HTML", disable_web_page_preview=True, reply_markup=board.as_markup())           
            asyncio.create_task(delete_message_after_delay(sent_message.chat.id, sent_message.message_id))

        elif callback_query.data.startswith("position:"):
            await callback_query.answer()
            position_id = callback_query.data.split(":")[2]
            status = callback_query.data.split(":")[1]
            if status == "activate":
                status = 'активна'
            else:
                status = 'неактивна'
            with sqlite3.connect(f'data/db/work db/warehouse_{region}.db') as con:
                cur = con.cursor()
                cur.execute(f'UPDATE Position SET status = ? WHERE id = {position_id}', [status])
                con.commit
            board = InlineKeyboardBuilder()
            board.row(types.InlineKeyboardButton(text="↪️Главное меню↩️", callback_data="OK"))
            sent_message = await callback_query.message.edit_text(f'<b>Статус профессии изменен</b>', parse_mode="HTML", disable_web_page_preview=True, reply_markup=board.as_markup())           
            await state.update_data(msg_id=sent_message.message_id)
            asyncio.create_task(delete_message_after_delay(sent_message.chat.id, sent_message.message_id))

        elif callback_query.data.startswith("addproff_"):
            await callback_query.answer()
            proff = callback_query.data.split("_")[1]
            with sqlite3.connect(f'data/db/work db/warehouse_{region}.db') as con:
                cur = con.cursor()
                proffession = (cur.execute('SELECT position FROM Position WHERE id = ?', [proff]).fetchone())[0]
            await state.update_data(proff=proffession)
            user_data = await state.get_data()
            msg_id = user_data['msg_id']
            full_name = user_data['full_name']
            fio = user_data['fio']
            text = (f'<b>ФИО:</b><i> {full_name} ({fio}</i>)\n'
                    f'<b>Должность:</b><i> {proffession}</i>\n'
                    '<i>Необходимо задать дату рождения</i>\n\n'
                    '<b>Выбери ГОД рождения</b>')
            await state.set_state(calendar.year)
            delta = 16
            years_range = 35
            years = my_calendar_year(delta, years_range)
            board = InlineKeyboardBuilder()
            for row in years:
                board.add(types.InlineKeyboardButton(text=f"{row}", callback_data=f"years_{row}")) 
            board.adjust(7, 7, 7, 7)
            board.row(types.InlineKeyboardButton(text="Ранее", callback_data=f"early_{delta}"))    
            board.row(types.InlineKeyboardButton(text="↪️Главное меню↩️", callback_data="OK"))    
            sent_message = await bot.edit_message_text(chat_id=user_id, message_id=msg_id, text=text, parse_mode="HTML", disable_web_page_preview=True, reply_markup=board.as_markup())          
            await state.update_data(msg_id=sent_message.message_id)
            asyncio.create_task(delete_message_after_delay(sent_message.chat.id, sent_message.message_id))
        
        elif callback_query.data.startswith("early_"):
            await callback_query.answer()
            delta = int(callback_query.data.split("_")[1])
            user_data = await state.get_data()
            msg_id = user_data['msg_id']
            full_name = user_data['full_name']
            fio = user_data['fio']
            proffession = user_data['proff']
            text = (f'<b>ФИО:</b><i> {full_name} ({fio}</i>)\n'
                    f'<b>Должность:</b><i> {proffession}</i>\n'
                    '<i>Необходимо задать дату рождения</i>\n\n'
                    '<b>Выбери ГОД рождения</b>')
            delta = delta + 35
            years_range = 35
            data = my_calendar_year(delta, years_range)
            board = InlineKeyboardBuilder()
            for row in data:
                board.add(types.InlineKeyboardButton(text=f"{row}", callback_data=f"years_{row}")) 
            board.adjust(7, 7, 7, 7)
            board.row(types.InlineKeyboardButton(text="Ранее", callback_data=f"early_{delta}"))    
            board.row(types.InlineKeyboardButton(text="↪️Главное меню↩️", callback_data="OK"))    
            sent_message = await bot.edit_message_text(chat_id=user_id, message_id=msg_id, text=text, parse_mode="HTML", disable_web_page_preview=True, reply_markup=board.as_markup())          
            await state.update_data(msg_id=sent_message.message_id)
            asyncio.create_task(delete_message_after_delay(sent_message.chat.id, sent_message.message_id))

        elif callback_query.data.startswith("years_"):
            await callback_query.answer()
            year = callback_query.data.split("_")[1]
            await state.update_data(year=year)
            user_data = await state.get_data()
            msg_id = user_data['msg_id']
            full_name = user_data['full_name']
            fio = user_data['fio']
            proffession = user_data['proff']
            text = (f'<b>ФИО:</b><i> {full_name} ({fio}</i>)\n'
                    f'<b>Должность:</b><i> {proffession}</i>\n'
                    '<i>Необходимо задать дату рождения</i>\n\n'
                    '<b>Выбери МЕСЯЦ рождения</b>')
            data = my_calendar_mounth()
            mounths = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']
            board = InlineKeyboardBuilder()
            for i in range(0, 12):
                board.add(types.InlineKeyboardButton(text=f"{mounths[i]}", callback_data=f"mounth_{data[i]}")) 
            board.adjust(3, 3, 3, 3)
            board.row(types.InlineKeyboardButton(text="↪️Главное меню↩️", callback_data="OK"))    
            sent_message = await bot.edit_message_text(chat_id=user_id, message_id=msg_id, text=text, parse_mode="HTML", disable_web_page_preview=True, reply_markup=board.as_markup())          
            await state.update_data(msg_id=sent_message.message_id)
            asyncio.create_task(delete_message_after_delay(sent_message.chat.id, sent_message.message_id))

        elif callback_query.data.startswith("mounth_"):
            await callback_query.answer()
            mounth = callback_query.data.split("_")[1]
            await state.update_data(mounth=mounth)
            user_data = await state.get_data()
            msg_id = user_data['msg_id']
            full_name = user_data['full_name']
            fio = user_data['fio']
            proffession = user_data['proff']
            text = (f'<b>ФИО:</b><i> {full_name} ({fio}</i>)\n'
                    f'<b>Должность:</b><i> {proffession}</i>\n'
                    '<i>Необходимо задать дату рождения</i>\n\n'
                    '<b>Выбери ДАТУ рождения</b>')
            data = my_calendar_day()
            board = InlineKeyboardBuilder()
            for row in data:
                board.add(types.InlineKeyboardButton(text=f"{row}", callback_data=f"day_{row}")) 
            board.adjust(5, 5, 5, 5, 5, 5, 1)
            board.row(types.InlineKeyboardButton(text="↪️Главное меню↩️", callback_data="OK"))    
            sent_message = await bot.edit_message_text(chat_id=user_id, message_id=msg_id, text=text, parse_mode="HTML", disable_web_page_preview=True, reply_markup=board.as_markup())          
            await state.update_data(msg_id=sent_message.message_id)
            asyncio.create_task(delete_message_after_delay(sent_message.chat.id, sent_message.message_id))

        elif callback_query.data.startswith("day_"):
            await callback_query.answer()
            day = callback_query.data.split("_")[1]
            user_data = await state.get_data()
            msg_id = user_data['msg_id']
            full_name = user_data['full_name']
            fio = user_data['fio']
            proffession = user_data['proff']
            date = day + '.' + user_data['mounth'] + '.' + user_data['year']
            await state.update_data(birthday=date)
            text = (f'<b>ФИО:</b><i> {full_name} ({fio}</i>)\n'
                    f'<b>Должность:</b><i> {proffession}</i>\n'
                    f'<b>Дата рождения:</b><i> {date}</i>\n'
                    '<b>Теперь необходимо выбрать <u>дату трудоустройства</u></b>\n\n'
                    '<u><b>Выбери ГОД (если трудоустройство происходит сегодня, то нажми соответстующую кнопку)</b></u>')
            delta = 0
            years_range = 6
            years = my_calendar_year(delta, years_range)
            board = InlineKeyboardBuilder()
            for row in years:
                board.add(types.InlineKeyboardButton(text=f"{row}", callback_data=f"hire-year_{row}")) 
            board.adjust(3, 3)
            board.row(types.InlineKeyboardButton(text="Сегодня", callback_data="hiretoday"))    
            board.row(types.InlineKeyboardButton(text="↪️Главное меню↩️", callback_data="OK"))    
            sent_message = await bot.edit_message_text(chat_id=user_id, message_id=msg_id, text=text, parse_mode="HTML", disable_web_page_preview=True, reply_markup=board.as_markup())          
            await state.update_data(msg_id=sent_message.message_id)
            asyncio.create_task(delete_message_after_delay(sent_message.chat.id, sent_message.message_id))

        elif callback_query.data.startswith("hiretoday"):
            await callback_query.answer()
            user_data = await state.get_data()
            msg_id = user_data['msg_id']
            full_name = user_data['full_name']
            fio = user_data['fio']
            proffession = user_data['proff']
            birthday = user_data['birthday']
            hire_date = datetime.now().strftime("%d.%m.%Y")
            await state.update_data(hire_date=hire_date)
            text = (f'<b>ФИО:</b><i> {full_name} ({fio}</i>)\n'
                    f'<b>Должность:</b><i> {proffession}</i>\n'
                    f'<b>Дата рождения:</b><i> {birthday}</i>\n'
                    f'<b>Дата трудоустройства:</b><i> {hire_date}</i>\n\n'
                    '<u><b>Введи номер и расположение шкафчика сотрудника <i>(например: 143 логистика)</i></b></u>')
            await state.set_state(employees.locker_number)
            board = InlineKeyboardBuilder()
            board.add(types.InlineKeyboardButton(text="↪️Главное меню↩️", callback_data="OK"))    
            sent_message = await bot.edit_message_text(chat_id=user_id, message_id=msg_id, text=text, parse_mode="HTML", disable_web_page_preview=True, reply_markup=board.as_markup())          
            await state.update_data(msg_id=sent_message.message_id)
            asyncio.create_task(delete_message_after_delay(sent_message.chat.id, sent_message.message_id))

        elif callback_query.data.startswith("hire-year_"):
            await callback_query.answer()
            year = callback_query.data.split("_")[1]
            await state.update_data(hire_year=year)
            user_data = await state.get_data()
            msg_id = user_data['msg_id']
            full_name = user_data['full_name']
            fio = user_data['fio']
            proffession = user_data['proff']
            birthday = user_data['birthday']
            text = (f'<b>ФИО:</b><i> {full_name} ({fio}</i>)\n'
                    f'<b>Должность:</b><i> {proffession}</i>\n'
                    f'<b>Дата рождения:</b><i> {birthday}</i>\n'
                    '<b>Теперь необходимо выбрать <u>дату трудоустройства</u></b>\n\n'
                    '<u><b>Выбери МЕСЯЦ</b></u>')
            data = my_calendar_mounth()
            
            mounths = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']
            board = InlineKeyboardBuilder()
            for i in range(0, 12):
                board.add(types.InlineKeyboardButton(text=f"{mounths[i]}", callback_data=f"hire-mounth_{data[i]}")) 
            board.adjust(3, 3)
            board.row(types.InlineKeyboardButton(text="↪️Главное меню↩️", callback_data="OK"))    
            sent_message = await bot.edit_message_text(chat_id=user_id, message_id=msg_id, text=text, parse_mode="HTML", disable_web_page_preview=True, reply_markup=board.as_markup())          
            await state.update_data(msg_id=sent_message.message_id)
            asyncio.create_task(delete_message_after_delay(sent_message.chat.id, sent_message.message_id))

        elif callback_query.data.startswith("hire-mounth_"):
            await callback_query.answer()
            mounth = callback_query.data.split("_")[1]
            await state.update_data(hire_mounth=mounth)
            user_data = await state.get_data()
            msg_id = user_data['msg_id']
            full_name = user_data['full_name']
            fio = user_data['fio']
            proffession = user_data['proff']
            birthday = user_data['birthday']
            text = (f'<b>ФИО:</b><i> {full_name} ({fio}</i>)\n'
                    f'<b>Должность:</b><i> {proffession}</i>\n'
                    f'<b>Дата рождения:</b><i> {birthday}</i>\n'
                    '<b>Теперь необходимо выбрать <u>дату трудоустройства</u></b>\n\n'
                    '<u><b>Выбери ДЕНЬ</b></u>')
            day = my_calendar_day()
            board = InlineKeyboardBuilder()
            for row in day:
                board.add(types.InlineKeyboardButton(text=f"{row}", callback_data=f"hire-day_{row}")) 
            board.adjust(5, 5, 5, 5, 5, 5, 1)
            board.row(types.InlineKeyboardButton(text="↪️Главное меню↩️", callback_data="OK"))    
            sent_message = await bot.edit_message_text(chat_id=user_id, message_id=msg_id, text=text, parse_mode="HTML", disable_web_page_preview=True, reply_markup=board.as_markup())          
            await state.update_data(msg_id=sent_message.message_id)
            asyncio.create_task(delete_message_after_delay(sent_message.chat.id, sent_message.message_id))
        
        elif callback_query.data.startswith("hire-day_"):
            await callback_query.answer()
            day = callback_query.data.split("_")[1]
            user_data = await state.get_data()
            hire_date = f"{day}.{user_data['hire_mounth']}.{user_data['hire_year']}"
            await state.update_data(hire_date=hire_date)
            msg_id = user_data['msg_id']
            full_name = user_data['full_name']
            fio = user_data['fio']
            proffession = user_data['proff']
            birthday = user_data['birthday']
           
            text = (f'<b>ФИО:</b><i> {full_name} ({fio}</i>)\n'
                    f'<b>Должность:</b><i> {proffession}</i>\n'
                    f'<b>Дата рождения:</b><i> {birthday}</i>\n'
                    f'<b>Дата трудоустройства:</b><i> {hire_date}</i>\n\n'
                    '<u><b>Введи номер и расположение шкафчика сотрудника <i>(например: 143 логистика)</i></b></u>')
            await state.set_state(employees.locker_number)
            board = InlineKeyboardBuilder()
            board.add(types.InlineKeyboardButton(text="↪️Главное меню↩️", callback_data="OK"))    
            sent_message = await bot.edit_message_text(chat_id=user_id, message_id=msg_id, text=text, parse_mode="HTML", disable_web_page_preview=True, reply_markup=board.as_markup())          
            await state.update_data(msg_id=sent_message.message_id)
            asyncio.create_task(delete_message_after_delay(sent_message.chat.id, sent_message.message_id))

        elif data == "newpersonphoto":
            await callback_query.answer()
            user_id = callback_query.from_user.id
            user_data = await state.get_data()
            msg_id = user_data['msg_id']
            await state.set_state(employees.newpersonphoto)
            board = InlineKeyboardBuilder()
            board.add(types.InlineKeyboardButton(text="↪️Главное меню↩️", callback_data="OK"))    
            sent_message = await bot.edit_message_text(chat_id=user_id, message_id=msg_id, text="Осталось сделать фотографию сотрудника\n\nЖду", parse_mode="HTML", disable_web_page_preview=True, reply_markup=board.as_markup())          
            await state.update_data(msg_id=sent_message.message_id)
            asyncio.create_task(delete_message_after_delay(sent_message.chat.id, sent_message.message_id))

        elif data == "warehouse":
            await callback_query.answer()
            await state.clear()
            with sqlite3.connect(f'data/db/work db/warehouse_{region}.db') as con:
                cur = con.cursor()
                cur.execute('''
                    CREATE TABLE IF NOT EXISTS materials(
                            id INTEGER PRIMARY KEY AUTOINCREMENT, 
                            category VARCHAR (100),
                            season VARCHAR (100),
                            name VARCHAR (100),
                            size VARCHAR (100),
                            quantity VARCHAR (100),
                            who_add VARCHAR (100)
                            )''')
                
                cur.execute('''
                    CREATE TABLE IF NOT EXISTS issued_materials(
                            id INTEGER PRIMARY KEY AUTOINCREMENT, 
                            material_id VARCHAR (100),
                            employee_id VARCHAR (100),
                            quantity VARCHAR (100),
                            issue_date VARCHAR (100),
                            who_give VARCHAR (100)
                            )''')
                
                cur.execute('''
                    CREATE TABLE IF NOT EXISTS logs(
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            who VARCHAR (100),
                            what VARCHAR (100)
                            )''')
                con.commit()
            board = InlineKeyboardBuilder()
            board.add(types.InlineKeyboardButton(text="Выдать ТМЦ", callback_data="warehouse_move"))
            board.add(types.InlineKeyboardButton(text="Добавить новое ТМЦ", callback_data="warehouse_add"))
            board.add(types.InlineKeyboardButton(text="Экспорт в excel", callback_data="warehouse_export"))
            board.add(types.InlineKeyboardButton(text="↪️Главное меню↩️", callback_data="OK"))
            board.adjust(1, 1, 1, 1)
            sent_message = await callback_query.message.edit_text ('Выбери нужный пункт', parse_mode="HTML", disable_web_page_preview=True, reply_markup=board.as_markup())
            asyncio.create_task(delete_message_after_delay(sent_message.chat.id, sent_message.message_id))

        elif data == "warehouse_move":
            await callback_query.answer(text='🙅‍♂️ Еще не реализовано', show_alert=True, cache_time=5)  # Время кэширования ответа в секундах  # False - тост внизу, True - модальное окно
        elif data == "warehouse_add":
            await callback_query.answer(text='🙅‍♂️ Еще не реализовано', show_alert=True, cache_time=5)  # Время кэширования ответа в секундах  # False - тост внизу, True - модальное окно
        elif data == "warehouse_export":
            await callback_query.answer(text='🙅‍♂️ Еще не реализовано', show_alert=True, cache_time=5)  # Время кэширования ответа в секундах  # False - тост внизу, True - модальное окно


        elif data == "task":
            await callback_query.answer()
            await state.clear()
            with sqlite3.connect(f'data/db/work db/warehouse_{region}.db') as con:
                cur = con.cursor()
                cur.execute('''
                    CREATE TABLE IF NOT EXISTS tasks(
                            id INTEGER PRIMARY KEY AUTOINCREMENT, 
                            who_add VARCHAR (100), 
                            who_add_name VARCHAR (100),
                            to_whom VARCHAR (100),
                            to_whom_name VARCHAR (100),
                            time_start VARCHAR (100),
                            time_end VARCHAR (100), 
                            task VARCHAR (100), 
                            status VARCHAR (100),
                            finish BLOB
                            )''')
                con.commit()
            board = InlineKeyboardBuilder()
            board.row(types.InlineKeyboardButton(text="Создать задачу", callback_data="addtask"))    
            board.row(types.InlineKeyboardButton(text="Мои активные задания", callback_data="mytask"))    
            board.row(types.InlineKeyboardButton(text="Выданные мной задания", callback_data="megivetask"))   
            board.row(types.InlineKeyboardButton(text="↪️Главное меню↩️", callback_data="OK"))
            sent_message = await callback_query.message.edit_text (f"<i>Выбери нужный пункт</i>", parse_mode="HTML", disable_web_page_preview=True, reply_markup=board.as_markup())          
            asyncio.create_task(delete_message_after_delay(sent_message.chat.id, sent_message.message_id))   

        elif data == "addtask":
            await callback_query.answer()
            user_id = callback_query.from_user.id
            await state.clear()
            await state.set_state(worktask.addtask)
            await state.update_data(region=region, user_id=user_id)
            board = InlineKeyboardBuilder()
            board.add(types.InlineKeyboardButton(text="↪️Главное меню↩️", callback_data="OK"))
            sent_message = await callback_query.message.edit_text (f"<i>Вводи текст задания или иди в главное меню для отмены</i>", parse_mode="HTML", disable_web_page_preview=True, reply_markup=board.as_markup())          
            await state.update_data(msg_id=sent_message.message_id)
            asyncio.create_task(delete_message_after_delay(sent_message.chat.id, sent_message.message_id))   

        elif callback_query.data.startswith("add_task:"):
            await callback_query.answer()
            to_whom_idtg = callback_query.data.split(":")[1]
            to_whom_name = callback_query.data.split(":")[2]
            await state.update_data(to_whom_idtg=to_whom_idtg, to_whom_name=to_whom_name)
            user_data = await state.get_data()
            task = user_data['task']
            text = f'{task}\n\n<i>Задание для {to_whom_name}</i>\nВерно?'
            board = InlineKeyboardBuilder()
            board.row(types.InlineKeyboardButton(text="Верно", callback_data="add_task_OK"))
            board.row(types.InlineKeyboardButton(text="↪️Главное меню↩️", callback_data="OK"))
            sent_message = await callback_query.message.edit_text (f"{text}", parse_mode="HTML", disable_web_page_preview=True, reply_markup=board.as_markup())          
            await state.update_data(msg_id=sent_message.message_id)
            asyncio.create_task(delete_message_after_delay(sent_message.chat.id, sent_message.message_id)) 

        elif data == "add_task_OK":
            await callback_query.answer()
            user_id = callback_query.from_user.id
            name = callback_query.from_user.first_name
            user_data = await state.get_data()
            task = user_data['task']
            region = user_data['region']
            to_whom_idtg = user_data['to_whom_idtg']
            to_whom_name = user_data['to_whom_name']
            await state.clear()
            current_time = datetime.now()
            formatted_time = current_time.strftime('%d.%m.%Y %H:%M')
            status = 'active'
            with sqlite3.connect(f'data/db/work db/warehouse_{region}.db') as con:
                cur = con.cursor()
                cur.execute('INSERT INTO tasks (who_add, who_add_name, to_whom, to_whom_name, task, time_start, status) VALUES (?, ?, ?, ?, ?, ?, ?)', (user_id, name, to_whom_idtg, to_whom_name, task, formatted_time, status))
                con.commit()
                task_id = cur.execute("SELECT id FROM tasks ORDER BY id DESC LIMIT 1")
                task_id = (cur.fetchone())[0]
                who_logs = who_did(user_id)
                cur.execute('INSERT INTO logs (who, what) VALUES (?, ?)', (who_logs, f"Добавил задание ID {task_id}"))
                con.commit()
            try:   
                board1 = InlineKeyboardBuilder()             
                board1.add(types.InlineKeyboardButton(text=f"Посмотреть", callback_data=f"check_task:{task_id}"))   
                await bot.send_message(to_whom_idtg, f"<i>Привет, {to_whom_name}!!!</i>\n{name} создал для тебя новое задание", parse_mode="HTML", disable_web_page_preview=True, reply_markup=board1.as_markup())
                text = "Уведомление о новом задании доставлено"
            except Exception as e:
                text = f"Уведомление о задании не удалось доставить, ошибка {e}"
            board = InlineKeyboardBuilder()
            board.add(types.InlineKeyboardButton(text="↪️Главное меню↩️", callback_data="OK"))    
            sent_message = await callback_query.message.edit_text (f"Задание оформлено\n{text}", parse_mode="HTML", disable_web_page_preview=True, reply_markup=board.as_markup())          
            asyncio.create_task(delete_message_after_delay(sent_message.chat.id, sent_message.message_id)) 

        elif data == "mytask":
            await callback_query.answer()
            await state.clear()
            user_id = callback_query.from_user.id
            name = callback_query.from_user.first_name
            with sqlite3.connect(f'data/db/work db/warehouse_{region}.db') as con:
                cur = con.cursor()
                tasks = cur.execute('SELECT id, task, who_add_name FROM tasks WHERE status = ?', ['active']).fetchall() 
            text = ''
            board = InlineKeyboardBuilder()
            for task in tasks:
                text += f'{task[0]}) {task[1]}\nПоручение от {task[2]}\n\n'
                board.add(types.InlineKeyboardButton(text=f"Задание {task[0]}", callback_data=f"check_task:{task[0]}"))
            board.adjust(*[3] * len(tasks), 1)
            board.row(types.InlineKeyboardButton(text="↪️Главное меню↩️", callback_data="OK"))
            sent_message = await callback_query.message.edit_text (f"{text}", parse_mode="HTML", disable_web_page_preview=True, reply_markup=board.as_markup())          
            asyncio.create_task(delete_message_after_delay(sent_message.chat.id, sent_message.message_id)) 

        elif callback_query.data.startswith("check_task:"):
            await callback_query.answer()
            task_id = callback_query.data.split(":")[1]
            with sqlite3.connect(f'data/db/work db/warehouse_{region}.db') as con:
                cur = con.cursor()
                result = cur.execute('SELECT who_add_name, task FROM tasks WHERE id = ?', [task_id]).fetchone()
            who_add_name, task = result
            board = InlineKeyboardBuilder()
            board.add(types.InlineKeyboardButton(text="Завершить", callback_data=f"task_complite:{task_id}")) 
            board.add(types.InlineKeyboardButton(text="↪️Главное меню↩️", callback_data="OK"))    
            sent_message = await callback_query.message.edit_text (f"{task}\nЗадание от {who_add_name}\n\nВыбирай нужный пункт", parse_mode="HTML", disable_web_page_preview=True, reply_markup=board.as_markup())          
            asyncio.create_task(delete_message_after_delay(sent_message.chat.id, sent_message.message_id)) 

        elif callback_query.data.startswith("task_complite:"):
            await callback_query.answer()
            task_id = callback_query.data.split(":")[1]
            await state.set_state(worktask.finish_task)
            with sqlite3.connect(f'data/db/work db/warehouse_{region}.db') as con:
                cur = con.cursor()
                result = cur.execute('SELECT who_add, to_whom_name, task FROM tasks WHERE id = ?', [task_id]).fetchone() 
            who_add, to_whom_name, task = result
            await state.update_data(who_add=who_add, to_whom_name=to_whom_name, region=region, task=task, task_id=task_id)
            board = InlineKeyboardBuilder()
            board.add(types.InlineKeyboardButton(text="↪️Главное меню↩️", callback_data="OK"))    
            sent_message = await callback_query.message.edit_text (f"Для завершения необходимо приложить фотоотчет.\n\nЖду фото", parse_mode="HTML", disable_web_page_preview=True, reply_markup=board.as_markup())          
            await state.update_data(msg_id=sent_message.message_id)
            asyncio.create_task(delete_message_after_delay(sent_message.chat.id, sent_message.message_id)) 

        elif callback_query.data.startswith("task_end:"):
            await callback_query.answer()
            task_id = callback_query.data.split(":")[1]
            user_id = callback_query.data.split(":")[2]
            current_time = datetime.now()
            formatted_time = current_time.strftime('%d.%m.%Y %H:%M')
            with sqlite3.connect(f'data/db/work db/warehouse_{region}.db') as con:
                cur = con.cursor()
                cur.execute(f'UPDATE tasks SET status = ?, time_end = ? WHERE id = {task_id}', ['finish', formatted_time])
                con.commit()
            await callback_query.message.delete()
            try:   
                await bot.send_message(user_id, text=f"Задание №{task_id} принято.", parse_mode="HTML", disable_web_page_preview=True)
                text = "Исполнитель проинформирован"
            except Exception as e:
                text = f"Исполнитель непроинформирован, ошибка {e}"
            sent_message = await bot.send_message(callback_query.from_user.id, text=f"Задание отмечено принятым\n{text}", parse_mode="HTML", disable_web_page_preview=True)          
            asyncio.create_task(delete_message_after_delay(sent_message.chat.id, sent_message.message_id)) 
            
        elif callback_query.data.startswith("task_not:"):
            await callback_query.answer()
            task_id = callback_query.data.split(":")[1]
            user_id = callback_query.data.split(":")[2]
            await callback_query.message.delete()
            try:   
                await bot.send_message(user_id, text=f"Задание №{task_id} непринято.", parse_mode="HTML", disable_web_page_preview=True)
                text = "Исполнитель проинформирован"
            except Exception as e:
                text = f"Исполнитель непроинформирован, ошибка {e}"
            sent_message = await bot.send_message(callback_query.from_user.id, text=f"Задание отмечено непринятым\n{text}", parse_mode="HTML", disable_web_page_preview=True)          
            asyncio.create_task(delete_message_after_delay(sent_message.chat.id, sent_message.message_id)) 

        elif data == "megivetask":
            await callback_query.answer(text='🙅‍♂️ Еще не реализовано', show_alert=True, cache_time=5)  # Время кэширования ответа в секундах  # False - тост внизу, True - модальное окно


    else:
        sent_message = await callback_query.message.edit_text (f"Вы не зарегистрированы", parse_mode="HTML")
        asyncio.create_task(delete_message_after_delay(sent_message.chat.id, sent_message.message_id))


# Календарь
def my_calendar_year(delta, years_range):
    current_datetime = datetime.now()
    year = int(current_datetime.year)
    year = year - delta
    years = []
    for row in range (years_range):
        years.append(year)
        year = year - 1
    return years
def my_calendar_mounth():
    mounths = [f"{i:02d}" for i in range(1, 13)]
    return mounths
def my_calendar_day():
    day = [f"{i:02d}" for i in range(1, 32)]
    return day

def format_date(date_str):
    if not date_str:
        return "Не указана"
    try:
    # Убираем лишние пробелы и преобразуем
        date_str = date_str.strip()
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj.strftime("%d.%m.%Y")
    except (ValueError, AttributeError):
    # Если формат не совпадает, возвращаем как есть
        return date_str

# Ввод текста задания
@dp.message(worktask.addtask)
async def add_task(message: Message, state: FSMContext):
    user_data = await state.get_data()
    msg_id = user_data['msg_id']
    if is_pure_text_message(message):
        user_id = user_data['user_id']
        region = user_data['region']
        await state.update_data(task=message.text)
        await message.delete()
        with sqlite3.connect(f'data/db/role.db') as con:
            cur = con.cursor()
            result = cur.execute('SELECT us_idtg, us_name FROM users WHERE us_region = ?', [region]).fetchall()
        board = InlineKeyboardBuilder()
        for row in result:
            board.row(types.InlineKeyboardButton(text=f"{row[1]}", callback_data=f"add_task:{row[0]}:{row[1]}"))
        board.row(types.InlineKeyboardButton(text="↪️Главное меню↩️", callback_data="OK"))   
        sent_message = await bot.edit_message_text(chat_id=user_id, message_id=msg_id, text="Выбирай, кому поставить задачу", parse_mode="HTML", disable_web_page_preview=True, reply_markup=board.as_markup())           
        await state.update_data(msg_id=sent_message.message_id)
        asyncio.create_task(delete_message_after_delay(sent_message.chat.id, sent_message.message_id))
    else:
        await message.delete()
        board = InlineKeyboardBuilder()
        board.add(types.InlineKeyboardButton(text="↪️Главное меню↩️", callback_data="OK"))
        sent_message = await bot.edit_message_text(chat_id=user_id, message_id=msg_id, text="<i>Пожалуйста, только текст</i>", parse_mode="HTML", disable_web_page_preview=True, reply_markup=board.as_markup())           
        asyncio.create_task(delete_message_after_delay(sent_message.chat.id, sent_message.message_id))

@dp.message(worktask.finish_task)
async def finish_task(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if is_image_message(message):
        user_data = await state.get_data()
        region = user_data['region']
        msg_id = user_data['msg_id']
        task = user_data['task']
        to_whom_name = user_data['to_whom_name']
        who_add = user_data['who_add']
        task_id = user_data['task_id']
        photo = message.photo[-1]  # Берем фото с самым высоким разрешением
        file_id = photo.file_id
        file = await bot.get_file(file_id)
        file_path = file.file_path
        download_path = os.path.join('data/temp', f"image_{user_id}.jpg")
        await bot.download_file(file_path, destination=download_path)
        scr = FSInputFile(f"data/temp/image_{user_id}.jpg")
        text = (f'Задание для {to_whom_name}:\n'
                f'{task}\n'
                'Выполнено. Прошу принять по фотоотчету')
        save_finish_photo(user_id, region, task_id)
        try:
            board1 = InlineKeyboardBuilder()
            board1.add(types.InlineKeyboardButton(text="Принять", callback_data=f"task_end:{task_id}:{user_id}"))
            board1.add(types.InlineKeyboardButton(text="Отклонить", callback_data=f"task_not:{task_id}:{user_id}"))
            send_photo = await bot.send_photo(chat_id=who_add, photo=scr, caption=text, parse_mode="HTML", reply_markup=board1.as_markup())
            text = "Уведомление о выполнении задания доставлено"
        except Exception as e:
            text = f"Уведомление о выполнении задания не доставлено.\nОшибка {e}"
        await message.delete()
        board = InlineKeyboardBuilder()
        board.add(types.InlineKeyboardButton(text="↪️Главное меню↩️", callback_data="OK"))
        sent_message = await bot.edit_message_text(chat_id=user_id, message_id=msg_id, text="Задание будет завершено после принятия инициатором", parse_mode="HTML", disable_web_page_preview=True, reply_markup=board.as_markup())           
        asyncio.create_task(delete_message_after_delay(sent_message.chat.id, sent_message.message_id))
    else:
        await message.delete()
        board = InlineKeyboardBuilder()
        board.add(types.InlineKeyboardButton(text="↪️Главное меню↩️", callback_data="OK"))
        sent_message = await bot.edit_message_text(chat_id=user_id, message_id=msg_id, text="<i>Прошу, фотоотчет</i>", parse_mode="HTML", disable_web_page_preview=True, reply_markup=board.as_markup())           
        asyncio.create_task(delete_message_after_delay(sent_message.chat.id, sent_message.message_id))

# Ввод номера шкафчика
@dp.message(employees.locker_number)
async def employees_locker_number(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_data = await state.get_data()
    fio = user_data['fio']
    full_name = user_data['full_name']
    proffession = user_data['proff']
    birthday = user_data['birthday']
    hire_date = user_data['hire_date']
    new_data = message.text
    msg_id = user_data['msg_id']
    await state.update_data(locker_number=new_data)
    await message.delete()
    text = (f'<b>ФИО:</b><i> {full_name} ({fio}</i>)\n'
                f'<b>Должность:</b><i> {proffession}</i>\n'
                f'<b>Дата рождения:</b><i> {birthday}</i>\n'
                f'<b>Дата трудоустройства:</b><i> {hire_date}</i>\n'
                f'<b>Шкафчик:</b><i> {new_data}</i>\n\n'
                '<u><b>Введи номер договора</b></u>')
    await state.set_state(employees.dogovor)
    board = InlineKeyboardBuilder()
    board.add(types.InlineKeyboardButton(text="↪️Главное меню↩️", callback_data="OK"))   
    sent_message = await bot.edit_message_text(chat_id=user_id, message_id=msg_id, text=text, parse_mode="HTML", disable_web_page_preview=True, reply_markup=board.as_markup())           
    await state.update_data(msg_id=sent_message.message_id)
    asyncio.create_task(delete_message_after_delay(sent_message.chat.id, sent_message.message_id))
# Ввод договора
@dp.message(employees.dogovor)
async def employees_dogovor(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_data = await state.get_data()
    fio = user_data['fio']
    full_name = user_data['full_name']
    proffession = user_data['proff']
    birthday = user_data['birthday']
    hire_date = user_data['hire_date']
    locker_number = user_data['locker_number']
    new_data = message.text
    msg_id = user_data['msg_id']
    if is_pure_text_message(message):
        await state.update_data(dogovor=new_data)
        await message.delete()
        text = (f'<b>ФИО:</b><i> {full_name} ({fio}</i>)\n'
                    f'<b>Должность:</b><i> {proffession}</i>\n'
                    f'<b>Дата рождения:</b><i> {birthday}</i>\n'
                    f'<b>Дата трудоустройства:</b><i> {hire_date}</i>\n'
                    f'<b>Шкафчик:</b><i> {locker_number}</i>\n'
                    f'<b>Номер договора:</b><i> {new_data}</i>\n\n'
                    '<u><b>Введи основной номер телефона начиная с +7</b></u>')
        await state.set_state(employees.phone_main)
        board = InlineKeyboardBuilder()
        board.add(types.InlineKeyboardButton(text="↪️Главное меню↩️", callback_data="OK"))   
        sent_message = await bot.edit_message_text(chat_id=user_id, message_id=msg_id, text=text, parse_mode="HTML", disable_web_page_preview=True, reply_markup=board.as_markup())           
        await state.update_data(msg_id=sent_message.message_id)
        asyncio.create_task(delete_message_after_delay(sent_message.chat.id, sent_message.message_id))
    else:
        await message.delete()
        board = InlineKeyboardBuilder()
        board.add(types.InlineKeyboardButton(text="↪️Главное меню↩️", callback_data="OK"))
        sent_message = await bot.edit_message_text(chat_id=user_id, message_id=msg_id, text="<i>Вводи корректные новые данные</i>", parse_mode="HTML", disable_web_page_preview=True, reply_markup=board.as_markup())           
        asyncio.create_task(delete_message_after_delay(sent_message.chat.id, sent_message.message_id))
# Ввод основного номера телефона
@dp.message(employees.phone_main)
async def employees_phone_main(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_data = await state.get_data()
    fio = user_data['fio']
    full_name = user_data['full_name']
    proffession = user_data['proff']
    birthday = user_data['birthday']
    hire_date = user_data['hire_date']
    locker_number = user_data['locker_number']
    dogovor = user_data['dogovor']
    new_data = message.text
    msg_id = user_data['msg_id']
    if is_pure_text_message(message):
        await state.update_data(phone_main=new_data)
        await message.delete()
        text = (f'<b>ФИО:</b><i> {full_name} ({fio}</i>)\n'
                    f'<b>Должность:</b><i> {proffession}</i>\n'
                    f'<b>Дата рождения:</b><i> {birthday}</i>\n'
                    f'<b>Дата трудоустройства:</b><i> {hire_date}</i>\n'
                    f'<b>Шкафчик:</b><i> {locker_number}</i>\n'
                    f'<b>Номер договора:</b><i> {dogovor}</i>\n'
                    f'<b>Тел основной:</b><i> {new_data}</i>\n\n'
                    '<u><b>Введи дополнительный номер телефона начиная с +7</b></u>')
        await state.set_state(employees.phone_backup)
        board = InlineKeyboardBuilder()
        board.add(types.InlineKeyboardButton(text="↪️Главное меню↩️", callback_data="OK"))   
        sent_message = await bot.edit_message_text(chat_id=user_id, message_id=msg_id, text=text, parse_mode="HTML", disable_web_page_preview=True, reply_markup=board.as_markup())           
        await state.update_data(msg_id=sent_message.message_id)
        asyncio.create_task(delete_message_after_delay(sent_message.chat.id, sent_message.message_id))
    else:
        await message.delete()
        board = InlineKeyboardBuilder()
        board.add(types.InlineKeyboardButton(text="↪️Главное меню↩️", callback_data="OK"))
        sent_message = await bot.edit_message_text(chat_id=user_id, message_id=msg_id, text="<i>Вводи корректные новые данные</i>", parse_mode="HTML", disable_web_page_preview=True, reply_markup=board.as_markup())           
        asyncio.create_task(delete_message_after_delay(sent_message.chat.id, sent_message.message_id))
@dp.message(employees.phone_backup)
async def employees_phone_backup(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_data = await state.get_data()
    fio = user_data['fio']
    full_name = user_data['full_name']
    proffession = user_data['proff']
    birthday = user_data['birthday']
    hire_date = user_data['hire_date']
    locker_number = user_data['locker_number']
    dogovor = user_data['dogovor']
    phone_main = user_data['phone_main']
    new_data = message.text
    msg_id = user_data['msg_id']
    if is_pure_text_message(message):
        await state.update_data(phone_backup=new_data)
        await message.delete()
        text = (f'<b>ФИО:</b><i> {full_name} ({fio}</i>)\n'
                    f'<b>Должность:</b><i> {proffession}</i>\n'
                    f'<b>Дата рождения:</b><i> {birthday}</i>\n'
                    f'<b>Дата трудоустройства:</b><i> {hire_date}</i>\n'
                    f'<b>Шкафчик:</b><i> {locker_number}</i>\n'
                    f'<b>Номер договора:</b><i> {dogovor}</i>\n'
                    f'<b>Тел основной:</b><i> {phone_main}</i>\n'
                    f'<b>Тел дополнительный:</b><i> {new_data}</i>\n\n'
                    '<u><b>Введи ссылку на аккаунт телеграма</b></u>')
        await state.set_state(employees.tg_link)
        board = InlineKeyboardBuilder()
        board.add(types.InlineKeyboardButton(text="↪️Главное меню↩️", callback_data="OK"))   
        sent_message = await bot.edit_message_text(chat_id=user_id, message_id=msg_id, text=text, parse_mode="HTML", disable_web_page_preview=True, reply_markup=board.as_markup())           
        await state.update_data(msg_id=sent_message.message_id)
        asyncio.create_task(delete_message_after_delay(sent_message.chat.id, sent_message.message_id))
    else:
        await message.delete()
        board = InlineKeyboardBuilder()
        board.add(types.InlineKeyboardButton(text="↪️Главное меню↩️", callback_data="OK"))
        sent_message = await bot.edit_message_text(chat_id=user_id, message_id=msg_id, text="<i>Вводи корректные новые данные</i>", parse_mode="HTML", disable_web_page_preview=True, reply_markup=board.as_markup())           
        asyncio.create_task(delete_message_after_delay(sent_message.chat.id, sent_message.message_id))
@dp.message(employees.tg_link)
async def employees_tg_link(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_data = await state.get_data()
    fio = user_data['fio']
    full_name = user_data['full_name']
    proffession = user_data['proff']
    birthday = user_data['birthday']
    hire_date = user_data['hire_date']
    locker_number = user_data['locker_number']
    dogovor = user_data['dogovor']
    phone_main = user_data['phone_main']
    phone_backup = user_data['phone_backup']
    new_data = message.text
    msg_id = user_data['msg_id']
    if is_pure_text_message(message):
        await state.update_data(tg_link=new_data)
        await message.delete()
        text = (f'<b>ФИО:</b><i> {full_name} ({fio}</i>)\n'
                    f'<b>Должность:</b><i> {proffession}</i>\n'
                    f'<b>Дата рождения:</b><i> {birthday}</i>\n'
                    f'<b>Дата трудоустройства:</b><i> {hire_date}</i>\n'
                    f'<b>Шкафчик:</b><i> {locker_number}</i>\n'
                    f'<b>Номер договора:</b><i> {dogovor}</i>\n'
                    f'<b>Тел основной:</b><i> {phone_main}</i>\n'
                    f'<b>Тел дополнительный:</b><i> {phone_backup}</i>\n'
                    f'<b>Телеграмм:</b><i> {new_data}</i>\n\n'
                    'Перед записью проверь введенные данные на корректность')
        await state.set_state(employees.tg_link)
        board = InlineKeyboardBuilder()
        board.add(types.InlineKeyboardButton(text="✅Верно", callback_data=f"newpersonphoto"))
        board.add(types.InlineKeyboardButton(text="Ошибка❌", callback_data="personal_add"))
        board.add(types.InlineKeyboardButton(text="↪️Главное меню↩️", callback_data="OK"))  
        board.adjust(2, 1) 
        sent_message = await bot.edit_message_text(chat_id=user_id, message_id=msg_id, text=text, parse_mode="HTML", disable_web_page_preview=True, reply_markup=board.as_markup())           
        await state.update_data(msg_id=sent_message.message_id)
        asyncio.create_task(delete_message_after_delay(sent_message.chat.id, sent_message.message_id))
    else:
        await message.delete()
        board = InlineKeyboardBuilder()
        board.add(types.InlineKeyboardButton(text="↪️Главное меню↩️", callback_data="OK"))
        sent_message = await bot.edit_message_text(chat_id=user_id, message_id=msg_id, text="<i>Вводи корректные новые данные</i>", parse_mode="HTML", disable_web_page_preview=True, reply_markup=board.as_markup())           
        asyncio.create_task(delete_message_after_delay(sent_message.chat.id, sent_message.message_id))

# Добавление новой должности
@dp.message(prof.newadd)
async def prof_newadd(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_data = await state.get_data()
    msg_id = user_data['msg_id']
    if is_pure_text_message(message):
        await state.update_data(new_prof=message.text)
        await message.delete()
        board = InlineKeyboardBuilder()
        board.add(types.InlineKeyboardButton(text="✅Верно", callback_data=f"profession:add_{message.text}"))
        board.add(types.InlineKeyboardButton(text="Ошибка❌", callback_data="position_new"))
        board.add(types.InlineKeyboardButton(text="↪️Главное меню↩️", callback_data="OK"))
        board.adjust(2, 1)
        sent_message = await bot.edit_message_text(chat_id=user_id, message_id=msg_id, text=f"Новая должность - <i>{message.text}</i>\n\nВерно?", parse_mode="HTML", disable_web_page_preview=True, reply_markup=board.as_markup())           
        await state.update_data(msg_id=sent_message.message_id)
        asyncio.create_task(delete_message_after_delay(sent_message.chat.id, sent_message.message_id))
    else:
        await message.delete()
        board = InlineKeyboardBuilder()
        board.add(types.InlineKeyboardButton(text="↪️Главное меню↩️", callback_data="OK"))
        sent_message = await bot.edit_message_text(chat_id=user_id, message_id=msg_id, text="<i>Вводи корректные данные</i>", parse_mode="HTML", disable_web_page_preview=True, reply_markup=board.as_markup())           
        asyncio.create_task(delete_message_after_delay(sent_message.chat.id, sent_message.message_id))

# Список профессий в текстовом формате
def warehouse_position(region):
    with sqlite3.connect(f'data/db/work db/warehouse_{region}.db') as con:
        cur = con.cursor()
        positions = cur.execute("SELECT * FROM Position").fetchall()
    if positions:
        text = ''
        for position in positions:
            text += f'<i>{position[1]}, статус - <u>{position[2]}</u></i>\n'
        return text.strip()
    else:
        text = 'Нет должностей в базе! Для начала необходимо ввести нужные должности. Обратитесь к менеджеру проекта или к админу бота'
        return text

# Добавление нового сотрудника
@dp.message(employees.full_name)
async def full_name(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_data = await state.get_data()
    msg_id = user_data['msg_id']
    region = user_data['region']
    if is_pure_text_message(message):
        await state.update_data(full_name=message.text)
        await state.update_data(fio=convert_fio_to_short(message.text))
        await message.delete()
        board = InlineKeyboardBuilder()
        with sqlite3.connect(f'data/db/work db/warehouse_{region}.db') as con:
            cur = con.cursor()
            positions = cur.execute("SELECT * FROM Position").fetchall()
        for position in positions:
            board.row(types.InlineKeyboardButton(text=f"{position[1]}", callback_data=f"addproff_{position[0]}"))
        board.row(types.InlineKeyboardButton(text="↪️Главное меню↩️", callback_data="OK"))
        sent_message = await bot.edit_message_text(chat_id=user_id, message_id=msg_id, text=f"<b>ФИО:</b><i>{message.text} ({convert_fio_to_short(message.text)})</i>\nВыбери занимаемую должность", parse_mode="HTML", disable_web_page_preview=True, reply_markup=board.as_markup())           
        await state.update_data(msg_id=sent_message.message_id)
        asyncio.create_task(delete_message_after_delay(sent_message.chat.id, sent_message.message_id))
    else:
        await message.delete()
        board = InlineKeyboardBuilder()
        board.add(types.InlineKeyboardButton(text="↪️Главное меню↩️", callback_data="OK"))
        sent_message = await bot.edit_message_text(chat_id=user_id, message_id=msg_id, text="<i>Вводи корректные данные</i>", parse_mode="HTML", disable_web_page_preview=True, reply_markup=board.as_markup())           
        asyncio.create_task(delete_message_after_delay(sent_message.chat.id, sent_message.message_id))

# Редактирование заметок сотрудников
@dp.message(employees.notes)
async def change_notes(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_data = await state.get_data()
    emp_id = user_data['emp_id']
    region = user_data['region']
    new_data = message.text
    msg_id = user_data['msg_id']
    if is_pure_text_message(message):
        await message.delete()
        who_logs = who_did(user_id)
        with sqlite3.connect(f'data/db/work db/warehouse_{region}.db') as con:
            cur = con.cursor()
            result = cur.execute(f'SELECT fio, notes FROM employees WHERE id = ?', [emp_id]).fetchone()
            fio, notes = result
            notes += f'\n{new_data}'
            cur.execute(f'UPDATE employees SET notes = ? WHERE id = {emp_id}', [notes])
            cur.execute('INSERT INTO logs (who, what) VALUES (?, ?)', (who_logs, f"Добавил заметку у {fio}"))
            con.commit()
        
        board = InlineKeyboardBuilder()
        board.add(types.InlineKeyboardButton(text="Проверить", callback_data=f"employee_{emp_id}"))
        sent_message = await bot.edit_message_text(chat_id=user_id, message_id=msg_id, text="<i>Нажми кнопку, для проверки новых данных</i>", parse_mode="HTML", disable_web_page_preview=True, reply_markup=board.as_markup())           
        asyncio.create_task(delete_message_after_delay(sent_message.chat.id, sent_message.message_id))

    else:
        await message.delete()
        board = InlineKeyboardBuilder()
        board.add(types.InlineKeyboardButton(text="↪️Главное меню↩️", callback_data="OK"))
        sent_message = await bot.edit_message_text(chat_id=user_id, message_id=msg_id, text="<i>Вводи корректные новые данные</i>", parse_mode="HTML", disable_web_page_preview=True, reply_markup=board.as_markup())           
        asyncio.create_task(delete_message_after_delay(sent_message.chat.id, sent_message.message_id))

# Редактирование данных сотрудников
@dp.message(employees.new_data)
async def change_data(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_data = await state.get_data()
    emp_id = user_data['emp_id']
    table = user_data['table']
    region = user_data['region']
    new_data = message.text
    msg_id = user_data['msg_id']
    if is_pure_text_message(message):
        await message.delete()
        who_logs = who_did(user_id)
        with sqlite3.connect(f'data/db/work db/warehouse_{region}.db') as con:
            cur = con.cursor()
            cur.execute(f'UPDATE employees SET {table} = ? WHERE id = {emp_id}', [new_data])
            employee = cur.execute(f'SELECT fio FROM employees WHERE id = ?', [emp_id]).fetchone()
            cur.execute('INSERT INTO logs (who, what) VALUES (?, ?)', (who_logs, f"Замена {table} у {employee[0]}"))
            con.commit()
        
        board = InlineKeyboardBuilder()
        board.add(types.InlineKeyboardButton(text="Проверить", callback_data=f"employee_{emp_id}"))
        sent_message = await bot.edit_message_text(chat_id=user_id, message_id=msg_id, text="<i>Нажми кнопку, для проверки новых данных</i>", parse_mode="HTML", disable_web_page_preview=True, reply_markup=board.as_markup())           
        asyncio.create_task(delete_message_after_delay(sent_message.chat.id, sent_message.message_id))

    else:
        await message.delete()
        board = InlineKeyboardBuilder()
        board.add(types.InlineKeyboardButton(text="↪️Главное меню↩️", callback_data="OK"))
        sent_message = await bot.edit_message_text(chat_id=user_id, message_id=msg_id, text="<i>Вводи корректные новые данные</i>", parse_mode="HTML", disable_web_page_preview=True, reply_markup=board.as_markup())           
        asyncio.create_task(delete_message_after_delay(sent_message.chat.id, sent_message.message_id))

@dp.message(employees.photo)
#@dp.message(lambda message: message.photo)
async def change_photo(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if is_image_message(message):
        photo = message.photo[-1]  # Берем фото с самым высоким разрешением
        file_id = photo.file_id
        file = await bot.get_file(file_id)
        file_path = file.file_path
        download_path = os.path.join('data/temp', f"image_{user_id}.jpg")
        await bot.download_file(file_path, destination=download_path)
        image_path = f'data/temp/image_{user_id}.jpg'
        with open(image_path, 'rb') as file:
            ava = file.read()
        user_data = await state.get_data()
        region = user_data['region']
        emp_id = user_data['emp_id']
        msg_id = user_data['msg_id']
        who_logs = who_did(user_id)
        with sqlite3.connect(f'data/db/work db/warehouse_{region}.db') as con:
            cur = con.cursor()
            cur.execute(f'UPDATE employees SET photo = ? WHERE id = {emp_id}', [ava])
            employee = cur.execute(f'SELECT fio FROM employees WHERE id = ?', [emp_id]).fetchone()
            cur.execute('INSERT INTO logs (who, what) VALUES (?, ?)', (who_logs, f"Замена фотографии у {employee[0]}"))
            con.commit()
        await message.delete()
        board = InlineKeyboardBuilder()
        board.add(types.InlineKeyboardButton(text="Проверить", callback_data=f"employee_{emp_id}"))
        sent_message = await bot.edit_message_text(chat_id=user_id, message_id=msg_id, text="<i>Нажми кнопку, для проверки новых данных</i>", parse_mode="HTML", disable_web_page_preview=True, reply_markup=board.as_markup())           
        asyncio.create_task(delete_message_after_delay(sent_message.chat.id, sent_message.message_id))
    else:
        await message.delete()
        board = InlineKeyboardBuilder()
        board.add(types.InlineKeyboardButton(text="↪️Главное меню↩️", callback_data="OK"))
        sent_message = await bot.edit_message_text(chat_id=user_id, message_id=msg_id, text="<i>Вводи корректные новые данные</i>", parse_mode="HTML", disable_web_page_preview=True, reply_markup=board.as_markup())           
        asyncio.create_task(delete_message_after_delay(sent_message.chat.id, sent_message.message_id))

@dp.message(employees.newpersonphoto)
#@dp.message(lambda message: message.photo)
async def add_newpersonphoto(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if is_image_message(message):
        photo = message.photo[-1]  # Берем фото с самым высоким разрешением
        file_id = photo.file_id
        file = await bot.get_file(file_id)
        file_path = file.file_path
        download_path = os.path.join('data/temp', f"image_{user_id}.jpg")
        await bot.download_file(file_path, destination=download_path)
        image_path = f'data/temp/image_{user_id}.jpg'
        with open(image_path, 'rb') as file:
            photo = file.read()
        user_data = await state.get_data()
        region = user_data['region']
        msg_id = user_data['msg_id']
        fio = user_data['fio']
        full_name = user_data['full_name']
        position = user_data['proff']
        birthday = user_data['birthday']
        birthday = datetime.strptime(birthday, "%d.%m.%Y")
        birthday = birthday.strftime("%Y-%m-%d")
        hire_date = user_data['hire_date']
        hire_date = datetime.strptime(hire_date, "%d.%m.%Y")
        hire_date = hire_date.strftime("%Y-%m-%d")
        locker_number = user_data['locker_number']
        dogovor = user_data['dogovor']
        phone_main = user_data['phone_main']
        phone_backup = user_data['phone_backup']
        msg_id = user_data['msg_id']
        tg_link = user_data['tg_link']
        await state.clear()
        who_add = who_did(user_id)
        with sqlite3.connect(f'data/db/work db/warehouse_{region}.db') as con:
            cur = con.cursor()
            emp_id = int(cur.execute('SELECT id FROM employees ORDER BY id DESC LIMIT 1').fetchone()[0])
            emp_id = emp_id + 1
            cur.execute(f'INSERT INTO employees (full_name, fio, position, birthday, hire_date, locker_number, dogovor, phone_main, phone_backup, tg_link, who_add, photo) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (full_name, fio, position, birthday, hire_date, locker_number, dogovor, phone_main, phone_backup, tg_link, who_add, photo))
            cur.execute(f'INSERT INTO logs (who, what) VALUES (?, ?)', (who_add, f'Добавил {full_name}'))
            con.commit()
        await message.delete()
        board = InlineKeyboardBuilder()
        board.add(types.InlineKeyboardButton(text="↪️Главное меню↩️", callback_data="OK"))
#        board.add(types.InlineKeyboardButton(text="Проверить", callback_data=f"employee_{emp_id}"))
        sent_message = await bot.edit_message_text(chat_id=user_id, message_id=msg_id, text=f"<b>{full_name} добавлен</b>", parse_mode="HTML", disable_web_page_preview=True, reply_markup=board.as_markup())          
        await state.update_data(msg_id=sent_message.message_id)
        asyncio.create_task(delete_message_after_delay(sent_message.chat.id, sent_message.message_id))
    
    else:
        await message.delete()
        board = InlineKeyboardBuilder()
        board.add(types.InlineKeyboardButton(text="↪️Главное меню↩️", callback_data="OK"))
        sent_message = await bot.edit_message_text(chat_id=user_id, message_id=msg_id, text="<i>Вводи корректные новые данные</i>", parse_mode="HTML", disable_web_page_preview=True, reply_markup=board.as_markup())           
        asyncio.create_task(delete_message_after_delay(sent_message.chat.id, sent_message.message_id))

# Сохранение результата задачи в базу
def save_finish_photo(user_id, region, task_id):
    image_path = f'data/temp/image_{user_id}.jpg'
    with open(image_path, 'rb') as file:
        task_finish = file.read()
    with sqlite3.connect(f'data/db/work db/warehouse_{region}.db') as con:
        cur = con.cursor()
        cur.execute(f'UPDATE tasks SET finish = ? WHERE id = {task_id}', [task_finish])
        con.commit()



def who_did(user_id):
    with sqlite3.connect(f'data/db/role.db') as con:
        cur = con.cursor()
        result = cur.execute('SELECT us_idtg, us_name FROM users WHERE us_idtg = ?', [user_id]).fetchone()
    us_idtg, us_name = result
    result = us_idtg + ' ' + us_name
    return result

# Проверяет, является ли сообщение изображением
def is_image_message(message: types.Message) -> bool:
    return bool(message.photo)

# Проверяет, является ли сообщение именно текстовым (без медиа).
def is_pure_text_message(message: types.Message) -> bool:
    return bool(message.text and not (message.photo or message.video or 
                                     message.document or message.audio or 
                                     message.voice or message.sticker))

# Функция для получения сотрудников с пагинацией
def get_employees_page(page: int, region: str, status) -> Tuple[List[Tuple], int]:
    """Получение страницы сотрудников и общего количества"""
    offset = (page - 1) * ITEMS_PER_PAGE
    with sqlite3.connect(f'data/db/work db/warehouse_{region}.db') as con:
        cur = con.cursor()
        # Получаем сотрудников с статусом 'active' в алфавитном порядке
        employees = cur.execute('''
            SELECT id, fio, position 
            FROM employees 
            WHERE status = ? 
            ORDER BY full_name 
            LIMIT ? OFFSET ?
        ''', (status, ITEMS_PER_PAGE, offset)).fetchall()
        
        # Получаем общее количество активных сотрудников
        total_count = cur.execute('''
            SELECT COUNT(*) 
            FROM employees 
            WHERE status = ? 
        ''', (status,)).fetchone()[0]
    
    return employees, total_count

# Функция для форматирования сообщения
def format_employees_message(employees: List[Tuple], page: int, total_pages: int, total_count: int) -> str:
    """Форматирование сообщения со списком сотрудников"""
    if not employees:
        return "Нет активных сотрудников"
    message_text = "Выбери нужного сотрудника"
    return message_text

# Функция для создания клавиатуры пагинации
def create_pagination_keyboard(page: int, total_pages: int, employees: List[Tuple], status) -> types.InlineKeyboardMarkup:
    """Создание клавиатуры с сотрудниками и пагинацией"""
    keyboard = InlineKeyboardBuilder()
    
    # Добавляем кнопки сотрудников
    for emp_id, fio, position in employees:
        keyboard.add(types.InlineKeyboardButton(
            text=f"{fio}",
            callback_data=f"employee_{emp_id}"
        ))
    
    keyboard.adjust(2)  # По одной кнопке в строке
    
    # Добавляем кнопки пагинации
    nav_buttons = []
    if page > 1:
        nav_buttons.append(types.InlineKeyboardButton(
            text="◀️ Назад",
            callback_data=f"page_{page-1}_{status}"
        ))
    
    nav_buttons.append(types.InlineKeyboardButton(
        text=f"{page}/{total_pages}",
        callback_data="current_page"
    ))
    
    if page < total_pages:
        nav_buttons.append(types.InlineKeyboardButton(
            text="Вперед ▶️",
            callback_data=f"page_{page+1}_{status}"
        ))
    
    if nav_buttons:
        keyboard.row(*nav_buttons)
    
    # Добавляем кнопку возврата
    keyboard.row(types.InlineKeyboardButton(text="↪️ Назад в меню персонала", callback_data="personal"))
    
    return keyboard.as_markup()

# Функция для отображения страницы сотрудников
async def show_employees_page(callback_query: types.CallbackQuery, page: int, region: str, status):
    """Отображение страницы с сотрудниками"""
    employees, total_count = get_employees_page(page, region, status)
    total_pages = (total_count + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
    
    if page > total_pages and total_pages > 0:
        page = total_pages
        employees, total_count = get_employees_page(page, region, status)
    
    message_text = format_employees_message(employees, page, total_pages, total_count)
    keyboard = create_pagination_keyboard(page, total_pages, employees, status)
    
    await callback_query.message.edit_text(
        text=message_text,
        reply_markup=keyboard,
        parse_mode='Markdown'
    )

# Проверка зарегистрирован пользователь или нет
def user_role(user_id: int):
    with sqlite3.connect('data/db/role.db') as con:
        cur = con.cursor()
        user_data = cur.execute('SELECT us_role FROM users WHERE us_idtg = ?', [user_id]).fetchone()
        if user_data:
            role = user_data[0]
            return role
        return None
    
# Проверка региона   
def user_region(user_id: int):
    with sqlite3.connect('data/db/role.db') as con:
        cur = con.cursor()
        user_data = cur.execute('SELECT us_region FROM users WHERE us_idtg = ?', [user_id]).fetchone()
        if user_data:
            region = user_data[0]
            return region
        return None

# Запись логов
def reg_log(region, user, text):
    with sqlite3.connect(f'data/db/work db/warehouse_{region}.db') as con:
        cur = con.cursor()
        cur.execute('INSERT INTO logs (who, what) VALUES (?, ?, ?)', (user, text))
        con.commit()

# Удаление сообщения после задержки
async def delete_message_after_delay(chat_id: int, message_id: int, delay: int = 600):
    await asyncio.sleep(delay)  # Задержка в секундах
    try:
        await bot.delete_message(chat_id, message_id)
    except Exception as e:
        logging.error(f"Не удалось удалить сообщение {chat_id}: {e}")

# Преобразование полного ФИО в краткое
def convert_fio_to_short(full_name: str) -> str:
    parts = full_name.split()
    if len(parts) < 3:
        return full_name
    surname = parts[0]  # Фамилия
    name = parts[1]     # Имя
    patronymic = parts[2]  # Отчество
    # Берем первую букву имени и отчества
    name_init = name[0].upper() + "."
    patronymic_init = patronymic[0].upper() + "."
    return f"{surname} {name_init}{patronymic_init}"

def update_data_role_DB(user_id, name):
    with sqlite3.connect(f'data/db/role.db') as con:
        cur = con.cursor()
        cur.execute(f'UPDATE users SET us_name = ? WHERE us_idtg = {user_id} ', [name])
        con.commit()

def check_personal(region):
    with sqlite3.connect(f'data/db/work db/warehouse_{region}.db') as con:
        cur = con.cursor()
        result_position = cur.execute('SELECT position FROM Position WHERE status = ?', ['активна']).fetchall()
        logging.info(f"{result_position}")   
        text = ""
        for position_tuple in result_position:
            position = position_tuple[0]
            result_employees = cur.execute(f'SELECT id FROM employees WHERE position = ? AND status = "active"', [position]).fetchall()
            data = len(result_employees)
            text += f'<i><u>{position}</u> - {data}</i>\n'
            logging.info(f"{text}")   
    return text


# Воркер для шедулера
async def schedule_worker():
    loop = asyncio.get_event_loop()
    # Запланированные задачи
#    schedule.every().day.at("08:00").do(lambda: asyncio.create_task(send_daily_report()))
#    schedule.every().hour.at(":00").do(lambda: asyncio.create_task(send_reminder()))
#    schedule.every(30).minutes.do(lambda: asyncio.create_task(check_tasks()))
    # Запускаем шедулер в отдельном потоке
    await loop.run_in_executor(None, run_schedule)

def run_schedule():
    """Запуск планировщика в отдельном потоке"""
    while True:
        schedule.run_pending()
        time.sleep(1)



# Запуск бота
async def main():
#    asyncio.create_task(schedule_worker())
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())