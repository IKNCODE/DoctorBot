![](https://liczejedvarsaulyanovsk-r73.gosweb.gosuslugi.ru/netcat_files/109/1316/medicina.png)
# DoctorBot
![Static Badge](https://img.shields.io/badge/python-3.12.4-blue)
![Static Badge](https://img.shields.io/badge/aiogram-3.3.0-green)
![Static Badge](https://img.shields.io/badge/release-1.1.2-red)



### Про DistrictBot
----
DistrictBot это телеграмм бот, с помощью которого можно воспользоваться следующими услугами:
- Функционал клиента:
  - Вызов врача на дом (по мед. полису или ФИО)
  - Запись на прием к врачу (в свободное время с выбором врача)
- Функционал врача:
  - Авторизация в систему по QR-Коду
  - Просмотр вызовов (возможность заверешния вызовов)
  - Отправка уведомлений другому сотруднику

Телеграмм-бот также имеет вхаимодействие с приложением DistrictDoctor, которые связаны между собой одной базой данных

### Установка
----
Установка через репозиторий GitHub:
```
git clone https://github.com/IKNCODE/DoctorBot.git
```

### Docker
----
Для создания Docker контейнера, нужно скачать [Image](https://clck.ru/3BE8bX) телеграмм-бота, и прописать следующую команду: 
```
docker pull ikncode/doctorbot
docker run -i -t 6f9fb287e7ad /bin/bash
```
