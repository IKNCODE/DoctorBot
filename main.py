from aiogram import Bot, Dispatcher, executor, types
import pyodbc
from aiogram.contrib.fsm_storage.memory import MemoryStorage


server = r"Server=DESKTOP-OC4UNCB;Database=DistrictDat;Trusted_Connection=True;"

TOKEN_API = "6506274690:AAEx5vZAoICHu7u4vSrxtjNCvqxkSUl6Xjs"

storage = MemoryStorage()
bot =Bot(token=TOKEN_API)
dp = Dispatcher(bot, storage=storage)

user = []
conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=DESKTOP-OC4UNCB;DATABASE=DistrictDat;Trusted_Connection=yes;')
cursor = conn.cursor()
cursor.execute("""
SELECT ФИО FROM Амбулаторная_карта
""")
row = cursor.fetchone()
print(row[0])

@dp.message_handler(commands=["start"])
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

if __name__ == '__main__':
    executor.start_polling(dispatcher=dp, skip_updates=True)