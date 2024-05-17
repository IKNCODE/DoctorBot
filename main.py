import asyncio
from datetime import datetime, timedelta
import logging
import sys
import cv2

from aiogram import Bot, Dispatcher, types, F
import pyodbc
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import ContentType
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.methods import DeleteWebhook
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from config import TOKEN_API, SQL_SERVER
import asyncio
from commands import get_all_calls, get_doctor, get_call, create_uved , ending_call, finding_amb, get_priems, get_priems_count, get_available_priems, create_priem, get_all_doctors, get_doc_byname, get_amb_bypolis

class DoctorState(StatesGroup):
    polis_input = State()
    ambcard_input = State()
    findamb_input = State()
    priem_input = State()
    address_input = State()
    name_input = State()
    report_input = State()
    result_input = State()
    againpolis_input = State()
    polisaddr_input = State()
    polisjabjab_input = State()
    polisselect_input = State()
    polisdoctor_input = State()
    polisfinal_input = State()
    polisOK_input = State()
    again_input = State()
    end_input = State()

class DoctorUved(StatesGroup):
    wait_doc = State()
    wait_mes = State()

class AuthState(StatesGroup):
    qr_input = State()
    password_input = State()
    auth_input = State()
    call_input = State()
    pacient_input = State()

storage = MemoryStorage()
bot =Bot(token=TOKEN_API)
dp = Dispatcher(storage=storage)

conn = pyodbc.connect(SQL_SERVER)

#Кнопки команды /help
btn1 = types.KeyboardButton(text="Вызов врача 🌡")
btn2 = types.KeyboardButton(text="Мед. карта 🗂")
btn3 = types.KeyboardButton(text="Запись 📝")

kb = [ [btn1, btn2, btn3] ]

ikb = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

datas = { 1: "09:00", 2: "09:30", 3: "10:00", 4: "10:30", 5: "11:00", 6: "11:30", 7: "12:00", 8: "12:30", 9: "13:00", 10: "13:30", 11: "14:00", 12: "14:30", 13: "15:00", 14: "15:30", 15: "16:00"}

#Кнопки для доктора
btn1 = types.KeyboardButton(text="Вызовы 🌡")
btn2 = types.KeyboardButton(text="Уведомление ✉️")

doc_kb = [ [btn1], [btn2] ]

doc_ikb = types.ReplyKeyboardMarkup(keyboard=doc_kb, resize_keyboard=True)

result = []

@dp.message(Command("help"))
async def help_cmd(message: types.Message):
    await bot.send_message(chat_id=message.from_user.id, text="Выберите команду:", reply_markup=ikb)

#-----------------------------------------------Doctor Functions--------------------------------------------------------

@dp.message(Command("doctor"))
async def help_cmd(message: types.Message, state: FSMContext):
    await bot.send_message(chat_id=message.from_user.id, text="Здравствуйте! Пожалуйста, просканируйте свой QR-Код, чтобы войти в свою систему:")
    await state.set_state(AuthState.qr_input)

@dp.message(AuthState.qr_input,F.content_type == ContentType.PHOTO)
async def qr_cmd(message: types.Message, state: FSMContext):
    file_name = f"qrs/{message.photo[-1].file_id}.jpg"
    await bot.download(message.photo[-1], destination=file_name)
    ph = cv2.imread(file_name)
    scale_percent = 20
    width = int(ph.shape[1] * scale_percent / 100)
    height = int(ph.shape[0] * scale_percent / 100)
    dim = (width, height)
    resized_ph = cv2.resize(ph, dim)
    detector = cv2.QRCodeDetector()
    val, a, v = detector.detectAndDecode(resized_ph)
    await state.update_data(id_number=val)
    auth_data = await state.get_data()
    try:
        doctor = await get_doctor(int(auth_data['id_number']))
        for i in doctor:
            result.append(i.doctor_id)
            result.append(i.name)
            result.append(i.password)
            await state.update_data(doc_id=i.doctor_id)
        print(result)
        if len(result) != 0:
            await bot.send_message(text="Напишите Пароль:", chat_id=message.from_user.id)
            await state.set_state(AuthState.password_input)
        else:
            await bot.send_message(text="Сотрудник не найден, попробуйте еще раз:", chat_id=message.from_user.id)
    except:
        await bot.send_message(text="Произошла ошибка, попробуйте позже", chat_id=message.from_user.id)
@dp.message(AuthState.password_input)
async def doctor_password_cmd(message: types.Message, state: FSMContext):
    if message.text == result[2]:
        await state.update_data(password=message.text)
        await state.update_data(name=result[1])
        await bot.send_message(text=f"Вход прошел успешно, добро пожаловать {result[1]}", chat_id=message.from_user.id, reply_markup=doc_ikb)
        await state.set_state(AuthState.auth_input)
    else:
        await bot.send_message(text="Неправильный пароль, попробуйте еще раз:", chat_id=message.from_user.id)
@dp.message(F.text == "commands")
async def backin(message: types.Message, state: FSMContext):
    try:
        await bot.send_message(text=f"добро пожаловать {result[1]}", chat_id=message.from_user.id, reply_markup=doc_ikb)
        await state.set_state(AuthState.auth_input)
    except:
        await bot.send_message(text="Вы не вошли в систему, напишите /doctor:", chat_id=message.from_user.id)


@dp.message(F.text == "Вызовы 🌡")
async def doctor_call_cmd(message: types.Message, state:FSMContext):
    doc_data = await state.get_data()
    call_kb = []
    all_calls = await get_all_calls(doc_data["doc_id"])
    btn2 = types.KeyboardButton(text=f"Назад")
    call_kb.append([btn2])
    for i in all_calls:
        btn1 = types.KeyboardButton(text=f"{i.pacient}")
        call_kb.append([btn1])
    call_ikb = types.ReplyKeyboardMarkup(keyboard=call_kb, resize_keyboard=True)
    await bot.send_message(chat_id=message.from_user.id, text="Вызовы на сегодня:", reply_markup=call_ikb)
    await state.set_state(AuthState.call_input)

@dp.message(AuthState.call_input)
async def acall_doctor_cmd(message: types.Message, state: FSMContext):
    pac = await get_call(message.text)
    pacient = []
    await state.update_data(call_id=pac[0].call_id)
    for i in pac:
        pacient.append(i.pacient)
        pacient.append(i.report)
        pacient.append(i.address)
    btn1 = types.KeyboardButton(text="Завершить")
    btn2 = types.KeyboardButton(text="Назад")
    pacient_kb = [ [btn1, btn2] ]
    pac_ikb = types.ReplyKeyboardMarkup(keyboard=pacient_kb, resize_keyboard=True)

    if pacient:
        await bot.send_message(text=f"Пациент: {pacient[0]}\n Жалоба пациента: {pacient[1]}\n Адрес: {pacient[2]}", chat_id=message.from_user.id, reply_markup=pac_ikb)
        await state.set_state(AuthState.pacient_input)
    else:
        await bot.send_message(text="Произошла ошибка", chat_id=message.from_user.id)

@dp.message(AuthState.pacient_input)
async def pacient_state_cmd(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        await doctor_call_cmd(message,state)
    if message.text == "Завершить":
        await end_call_cmd(message, state)


async  def end_call_cmd(message: types.Message, state: FSMContext):
    try:
        call_data = await state.get_data()
        await ending_call(call_data['call_id'])
        await message.answer("Успешно")
        await state.update_data(call_id=0)
        await doctor_call_cmd(message, state)
    except:
        await bot.send_message(text="Произошла ошибка", chat_id=message.from_user.id)


@dp.message(F.text == "Уведомление ✉️")
async def doctor_uved_cmd(message: types.Message, state:FSMContext):
    all_docs = await get_all_doctors()
    btn = types.KeyboardButton(text="Назад")
    akb = []
    akb.append([btn])
    for i in all_docs:
        btn = types.KeyboardButton(text=str(i.name))
        akb.append([btn])
    call_ikb = types.ReplyKeyboardMarkup(keyboard=akb, resize_keyboard=True)
    await bot.send_message(chat_id=message.from_user.id, text="Выберите, кому написать сообщение"
                                                              "\nУведомление придет в приложение пользователю:", reply_markup=call_ikb)
    await state.set_state(DoctorUved.wait_doc)

@dp.message(DoctorUved.wait_doc)
async def send_mes(message: types.Message, state: FSMContext):
    await state.update_data(doc=message.text)
    doc_ide = await get_doc_byname(message.text)
    await state.update_data(doc_id=doc_ide)
    await bot.send_message(text="напишите сообщение:", chat_id=message.from_user.id)
    await state.set_state(DoctorUved.wait_mes)

@dp.message(DoctorUved.wait_mes)
async def send_mes_fin(message: types.Message, state: FSMContext):
    try:
        await state.update_data(mess=message.text)
        call_data = await state.get_data()
        print(call_data['doc_id'])
        print(call_data['mess'])
        await create_uved(call_data['doc_id'], call_data['mess'])
        await bot.send_message(text="Успешно", chat_id=message.from_user.id)
    except:
        await bot.send_message(text="Произошла ошибка!", chat_id=message.from_user.id)


#-----------------------------------------------Client Functions--------------------------------------------------------
@dp.message(F.text == "Запись 📝")
async def doctor_cmd(message: types.Message, state: FSMContext):
    await bot.send_message(chat_id=message.from_user.id, text="Наберите номер своего полиса (16 цифр):", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(DoctorState.priem_input)

@dp.message(DoctorState.priem_input)
async def test2_cmd(message: types.Message, state: FSMContext):
    if message.text.isdigit() == True:
        if len(message.text) == 16 and get_amb_bypolis(message.text):
            pol_id = await get_amb_bypolis(message.text)
            await state.update_data(amb_id=pol_id)
            await bot.send_message(text="Напишите жалобу:", chat_id=message.from_user.id)
            await state.set_state(DoctorState.polisjabjab_input)
        else:
            await message.answer(text="В номере полиса находится 16 цифр! Попробуйте заново:")
    else:
        await message.answer(text="Введите цифры!")

@dp.message(DoctorState.polisjabjab_input)
async def address43_cmd(message: types.Message, state: FSMContext):
    await state.update_data(report=message.text)
    kb = []
    for i in range(0,15):
        data = str(datetime.now().date() + timedelta(days=i))
        btn = types.KeyboardButton(text=data)
        kb.append([btn])
    auth_kb = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await bot.send_message(text="Выберите время (ближайшие 14 дней):", chat_id=message.from_user.id, reply_markup=auth_kb)
    await state.set_state(DoctorState.polisselect_input)

@dp.message(DoctorState.polisselect_input)
async def address43_cmd(message: types.Message, state: FSMContext):
    c = await get_priems_count(message.text)
    kb = []
    await state.update_data(datee=message.text)
    await state.update_data(dateforsql=message.text.replace('-',''))
    user_data = await state.get_data()
    global datas
    btn = types.KeyboardButton(text="Назад")
    kb.append([btn])
    if (c >= 0 and c < 15):
        for i in range(1,15):
            data = await get_available_priems(user_data['datee'], datas[i])
            btn = types.KeyboardButton(text=str(data))
            kb.append([btn])

    auth_kb = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await bot.send_message(text="Выберите свободные часы:", chat_id=message.from_user.id, reply_markup=auth_kb)
    await state.set_state(DoctorState.polisdoctor_input)

@dp.message(DoctorState.polisdoctor_input)
async def address43_cmd(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    await state.update_data(fin_data=f'{user_data["dateforsql"]} {message.text}')
    kb = []
    all_docs = await get_all_doctors()
    btn = types.KeyboardButton(text="Назад")
    kb.append([btn])
    for i in all_docs:
        btn = types.KeyboardButton(text=str(i.name))
        kb.append([btn])
    auth_kb = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await bot.send_message(text="Выберите врача:", chat_id=message.from_user.id, reply_markup=auth_kb)
    await state.set_state(DoctorState.polisfinal_input)

@dp.message(DoctorState.polisfinal_input)
async def address43_cmd(message: types.Message, state: FSMContext):
    doc_id = await get_doc_byname(message.text)
    await state.update_data(doctor_id= doc_id)
    await state.update_data(doctor_name=message.text)
    user_data = await state.get_data()
    btn1 = types.KeyboardButton(text="Да")
    btn2 = types.KeyboardButton(text="Нет")
    kb = [[btn1], [btn2]]
    auth_kb = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await bot.send_message(text=f"Давайте проверим информацию: Прием к врачу {user_data['doctor_name']}\n на время {user_data['fin_data']}\n с жалобой {user_data['report']}", chat_id=message.from_user.id, reply_markup=auth_kb)
    await state.set_state(DoctorState.polisOK_input)

@dp.message(DoctorState.polisOK_input)
async def address43_cmd(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    doc_id = user_data['doctor_id']
    pac_id = user_data['amb_id']
    if message.text == "Да":
        #try:
        await create_priem(doc_id, pac_id, user_data['fin_data'],user_data['report'])
        await bot.send_message(text=f"Все прошло успешно", chat_id=message.from_user.id)
        #except:
        #    await bot.send_message(text=f"Произошла ошибка", chat_id=message.from_user.id)

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

@dp.message(F.text == "2️⃣ По амбулаторной карте")
async def medpolis2_cmd(message: types.Message, state: FSMContext):
    await test2_cmd(message, state)
@dp.message(DoctorState.polis_input)
async def test_cmd(message: types.Message, state: FSMContext):
    await bot.send_message(chat_id=message.from_user.id, text="Наберите номер своего полиса (16 цифр):", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(DoctorState.address_input)

@dp.message(DoctorState.ambcard_input) #По амбулаторной карте
async def test2_cmd(message: types.Message, state: FSMContext):
    await bot.send_message(chat_id=message.from_user.id, text="Наберите номер своего полиса (16 цифр):", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(DoctorState.findamb_input)

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

@dp.message(DoctorState.findamb_input)
async def address2_cmd(message: types.Message, state: FSMContext):
    if message.text.isdigit() == True:
        if len(message.text) == 16:
            await state.update_data(polis=message.text)
            user_data = await state.get_data()
            paci = await finding_amb(user_data['polis'])
            btn1 = types.KeyboardButton(text="✅ Да")
            btn2 = types.KeyboardButton(text="❌ Нет, это не я")
            kb = [[btn1], [btn2]]
            auth_kb = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
            await state.update_data(polis=paci[0].polis)
            await state.update_data(address=paci[0].address)
            await state.update_data(name=paci[0].name)
            await bot.send_message(text=f"Вы {paci[0].name}?", chat_id=message.from_user.id, reply_markup=auth_kb)
            await state.set_state(DoctorState.againpolis_input)
        else:
            await message.answer(text="В номере полиса находится 16 цифр! Попробуйте заново:")
    else:
        await message.answer(text="Введите цифры!")

@dp.message(DoctorState.againpolis_input)
async def address22_cmd(message: types.Message, state: FSMContext):
    if message.text == '✅ Да':
        await message.answer(text="Хорошо")
        await addressPolis_cmd(message,state)
    elif message.text == '❌ Нет, это не я':
        await bot.send_message(text="Попробуйте ввести полис сначала", chat_id=message.from_user.id)
        await test2_cmd(message, state)
    else:
        await bot.send_message(text="Нажмите на одну из 2 кнопок 🙏", chat_id=message.from_user.id)

@dp.message(DoctorState.name_input)
async def address_cmd(message: types.Message, state: FSMContext):
        await state.update_data(address=message.text)
        await bot.send_message(text="Напишите ФИО:", chat_id=message.from_user.id)
        await state.set_state(DoctorState.report_input)

@dp.message(DoctorState.report_input)
async def address43_cmd(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await bot.send_message(text="Напишите жалобу:", chat_id=message.from_user.id)
    await state.set_state(DoctorState.result_input)

@dp.message(DoctorState.report_input)
async def addressPolis_cmd(message: types.Message, state: FSMContext):
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
    try:
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
        await bot.send_message(text="Запись прошла успешно 🥳 Участковый врач приедет в ближайшее время!", chat_id=message.from_user.id, reply_markup=types.ReplyKeyboardRemove())
    except Exception as ex:
        print(ex.args)
        await bot.send_message(text="К сожалению, произошла ошибка 🤒", chat_id=message.from_user.id, reply_markup=types.ReplyKeyboardRemove())


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