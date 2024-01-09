import asyncio
from datetime import datetime
import logging
import sys

from aiogram import Bot, Dispatcher, types, F
import pyodbc
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.methods import DeleteWebhook
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

server = r"Server=DESKTOP-OC4UNCB;Database=DistrictDat;Trusted_Connection=True;"

TOKEN_API = "6506274690:AAEx5vZAoICHu7u4vSrxtjNCvqxkSUl6Xjs"

class DoctorState(StatesGroup):
    polis_input = State()
    address_input = State()
    name_input = State()
    report_input = State()
    result_input = State()
    again_input = State()
    end_input = State()

storage = MemoryStorage()
bot =Bot(token=TOKEN_API)
dp = Dispatcher(storage=storage)

user = []
conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=DESKTOP-OC4UNCB;DATABASE=DistrictDat;Trusted_Connection=yes;')
cursor = conn.cursor()
cursor.execute("""
SELECT ФИО FROM Амбулаторная_карта
""")
row = cursor.fetchone()
print(row[0])

#Кнопки команды /help
btn1 = types.KeyboardButton(text="Вызов врача 🌡")
btn2 = types.KeyboardButton(text="Мед. карта 🗂")
btn3 = types.KeyboardButton(text="Запись 📝")

kb = [ [btn1, btn2, btn3] ]

ikb = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


@dp.message(Command("help"))
async def help_cmd(message: types.Message):
    await bot.send_message(chat_id=message.from_user.id, text="Выберите команду:", reply_markup=ikb)

@dp.message(F.text == "Вызов врача 🌡")
async def doctor_cmd(message: types.Message):
    btn1 = types.KeyboardButton(text="1️⃣ По мед. полису")
    btn2 = types.KeyboardButton(text="2️⃣ По амбулаторной карте")
    kb = [[btn1], [btn2]]
    auth_kb = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await bot.send_message(chat_id=message.from_user.id, text="Выберите способ аутентификации:", reply_markup=auth_kb)

@dp.message(F.text == "1️⃣ По мед. полису")
async def medpolis_cmd(message: types.Message, state: FSMContext):
    await test_cmd(message,state)
@dp.message(DoctorState.polis_input)
async def test_cmd(message: types.Message, state: FSMContext):
    await bot.send_message(chat_id=message.from_user.id, text="Наберите номер своего полиса (16 цифр):")
    await state.set_state(DoctorState.address_input)

@dp.message(DoctorState.address_input)
async def address_cmd(message: types.Message, state: FSMContext):
    if message.text.isdigit() == True:
        if len(message.text) == 16:
            await state.update_data(polis=message.text)
            await bot.send_message(text="Напишите адрес:", chat_id=message.from_user.id)
            await state.set_state(DoctorState.name_input)
        else:
            await message.answer(text="В номере полиса находится 16 цифр! Попробуйте заново:")
    else:
        await message.answer(text="Введите цифры!")

@dp.message(DoctorState.name_input)
async def address_cmd(message: types.Message, state: FSMContext):
        await state.update_data(address=message.text)
        await bot.send_message(text="Напишите ФИО:", chat_id=message.from_user.id)
        await state.set_state(DoctorState.report_input)

@dp.message(DoctorState.report_input)
async def address_cmd(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await bot.send_message(text="Напишите жалобу:", chat_id=message.from_user.id)
    await state.set_state(DoctorState.result_input)

@dp.message(DoctorState.result_input)
async def address_cmd(message: types.Message, state: FSMContext):
    await state.update_data(report=message.text)
    user_data = await state.get_data()
    btn1 = types.KeyboardButton(text="Да 👍")
    btn2 = types.KeyboardButton(text="Нет 👎")
    kb = [[btn1], [btn2]]
    rep_kb = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await bot.send_message(text="Давайте проверим введенные данные:", chat_id=message.from_user.id)
    await bot.send_message(text=f"Ваше ФИО - {user_data['name']}\nВаш полис - {user_data['polis']}\nАдрес - {user_data['address']}\nЖалоба {user_data['report']}?", chat_id=message.from_user.id, reply_markup=rep_kb)
    await state.set_state(DoctorState.again_input)

@dp.message(DoctorState.again_input)
async def address_cmd(message: types.Message, state: FSMContext):
    if message.text == 'Нет 👎':
        await message.answer(text="Хорошо, давайте начнем сначала")
        await test_cmd(message,state)
    elif message.text == 'Да 👍':
        await bot.send_message(text="Отлично! Отправляем данные", chat_id=message.from_user.id)
        await end_cmd(message, state)
    else:
        await bot.send_message(text="Нажмите на одну из 2 кнопок 🙏", chat_id=message.from_user.id)

@dp.message(DoctorState.end_input)
async def end_cmd(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};SERVER=DESKTOP-OC4UNCB;DATABASE=DistrictDat;Trusted_Connection=yes;')
    cursor = conn.cursor()
    cursor.execute(f"""
        INSERT INTO Вызов
           (Пациент
           ,Жалоба
           ,Дата_вызова
           ,Статус
           ,Врач
           ,Адрес)
     VALUES
           ('{user_data["name"]}'
           ,'{user_data["report"]}'
           ,GETDATE()
           ,'Идет'
           ,{1}
           ,'{user_data["address"]}')
        """)
    cursor.commit()
    conn.close()


@dp.callback_query(lambda c: c.data and c.data.startswith('btnFunc'))
async def process_btn_func(callback_query: types.CallbackQuery):
    code = callback_query.data[-1]
    if code.isdigit():
        if code == 1:
            await bot.answer_callback_query(callback_query.id, text='Нажата первая кнопка')
        elif code == 1:
            await bot.answer_callback_query(callback_query.id, text='Нажата вторая кнопка')
        else:
            await bot.answer_callback_query(callback_query.id, text='Нажата вторая кнопка')
    await bot.send_message(callback_query.from_user.id, f'Нажата инлайн кнопка! code={code}')


@dp.message(Command("start"))
async def hi(message : types.Message):
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};SERVER=DESKTOP-OC4UNCB;DATABASE=DistrictDat;Trusted_Connection=yes;')
    cursor = conn.cursor()
    cursor.execute("""
    SELECT ФИО FROM Амбулаторная_карта
    """)
    row = cursor.fetchall()
    for i in range(len(row)):
        await bot.send_message(text=row[i][0], chat_id=message.from_user.id)
    conn.close()

async def main() -> None:
    await bot(DeleteWebhook(drop_pending_updates=True))
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())