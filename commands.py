import datetime
from dataclasses import dataclass
import pyodbc
from config import SQL_SERVER
import aiosqlite

@dataclass
class Doctor:
    doctor_id: int
    name: str
    login: str
    password: str
    sex: str
    email: str
    passport: str

@dataclass
class Calls:
    call_id: int
    pacient: str
    address: str
    report: str
    call_date: datetime.datetime
    Doctor: list[Doctor]


@dataclass
class Card:
    card_id: int
    name: str
    sex: str
    date_of_birth: datetime.datetime
    address: str
    passport: str
    polis: str

@dataclass
class Priem:
    priem_id: int
    Doctor: list[Doctor]
    Pacient: list[Card]
    zapis_date: datetime.datetime
    status: str
    report: str

async def get_all_doctors():
    docs = []
    with pyodbc.connect(SQL_SERVER) as db:
        cursor = db.cursor()
        with cursor.execute(f"""
        SELECT * FROM Сотрудник""") as row:
            for i in row:
                docs.append(Doctor(
                    doctor_id=i[0],
                    name=i[1],
                    login=i[2],
                    password=i[3],
                    sex=i[4],
                    email=i[5],
                    passport=i[6]
                ))
    return docs

async def get_doc_byname(name):
    nam = ""
    with pyodbc.connect(SQL_SERVER) as db:
        cursor = db.cursor()
        with cursor.execute(f"""
        SELECT * FROM Сотрудник WHERE ФИО = '{name}'""") as row:
            for i in row:
                nam = i[0]
    return nam

async def get_amb_bypolis(polis):
    nam = ""
    with pyodbc.connect(SQL_SERVER) as db:
        cursor = db.cursor()
        with cursor.execute(f"""
        SELECT * FROM Амбулаторная_карта WHERE Полис_ОМС = '{polis}'""") as row:
            for i in row:
                nam = i[0]
    return nam

async def get_all_calls(doc_id):
    calls = []
    with pyodbc.connect(SQL_SERVER) as db:
        cursor = db.cursor()
        with cursor.execute(f"""
        SELECT * FROM Вызов WHERE Врач = {doc_id} AND Статус = 'Идет'""") as row:
            for i in row:
                calls.append(Calls(
                    call_id=i[0],
                    pacient=i[1],
                    report=i[2],
                    call_date=i[3],
                    address=i[6],
                    Doctor=i[5]
                ))
    return calls

async def get_doctor(id):
    with pyodbc.connect(SQL_SERVER) as db:
        doctor = []
        cursor = db.cursor()
        with cursor.execute(f"""
        SELECT * FROM Сотрудник WHERE id_сотрудник = {id}
        """) as row:
            for i in row:
                doctor.append(Doctor(
                    doctor_id=i[0],
                    name=i[1],
                    login=i[2],
                    password=i[3],
                    sex=i[4],
                    email=i[5],
                    passport=i[6]
                    ))
    return doctor

async def get_call(pac_id):
    with pyodbc.connect(SQL_SERVER) as db:
        call = []
        cursor = db.cursor()
        with  cursor.execute(f"""
                SELECT * FROM Вызов WHERE Пациент = '{pac_id}' AND Статус = 'Идет'
                """) as row:
            for i in row:
                call.append(Calls(
                    call_id=i[0],
                    pacient=i[1],
                    address=i[6],
                    report=i[2],
                    call_date=i[3],
                    Doctor=i[5]
                    ))
    return call

async def get_priems():
    with pyodbc.connect(SQL_SERVER) as db:
        priem = []
        cursor = db.cursor()
        with  cursor.execute(f"""
                SELECT * FROM Прием """) as row:
            for i in row:
                priem.append(Priem(
                    priem_id=i[0],
                    Doctor=i[1],
                    Pacient=i[2],
                    zapis_date=i[3],
                    status=i[4],
                    report=i[5]))
    return priem

async def get_priems_count(data):
    with pyodbc.connect(SQL_SERVER) as db:
        priem = []
        cursor = db.cursor()
        with  cursor.execute(f"""
                SELECT DATEADD(dd, 0, DATEDIFF(dd, 0, Дата_записи)) FROM Прием""") as row:
            for i in row:
                if str(i[0].date()) == data:
                    priem.append(i[0])
    return len(priem)

async def get_available_priems(data, hours: dict):
    with pyodbc.connect(SQL_SERVER) as db:
        priem = ''
        cursor = db.cursor()
        with  cursor.execute(f"""
                SELECT Дата_записи FROM Прием""") as row:
            for i in row:
                if str(i[0].date()) == data and f"{i[0].strftime('%H:%M')}" == hours:
                    return ""
                else:
                    priem = hours
    return priem

async def ending_call(call_id: int):
    with pyodbc.connect(SQL_SERVER) as db:
        cursor = db.cursor()
        cursor.execute(f"""
                UPDATE Вызов SET Статус = 'Окончен' WHERE id_вызов LIKE {call_id}
                """)
        cursor.commit()

async def create_priem(doc_id, pac, date_zap,rep):
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};SERVER=DESKTOP-OC4UNCB;DATABASE=DistrictDat;Trusted_Connection=yes;')
    cursor = conn.cursor()
    cursor.execute(f"""
        INSERT INTO Прием
           (Врач
           ,Пациент
           ,Дата_записи
           ,Статус
           ,Жалоба
           )
     VALUES
           ({int(doc_id)}
           ,{int(pac)}
           ,CONVERT(DATETIME, '{date_zap}')
           ,'Ожидает'
           ,'{rep}')
        """)
    cursor.commit()
    conn.close()

async def finding_amb(amb_card: int):
    with pyodbc.connect(SQL_SERVER) as db:
        amb = []
        cursor = db.cursor()
        with cursor.execute(f"""
                    SELECT * FROM Амбулаторная_карта WHERE Полис_ОМС = {int(amb_card)}
                """) as row:
            for i in row:
                amb.append(Card(
                    card_id=i[0],
                    name=i[1],
                    sex = i[2],
                    date_of_birth = i[3],
                    address = i[4],
                    passport = i[5],
                    polis = i[6]
                ))
        cursor.commit()
    return amb






