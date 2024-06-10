FROM python:3.12.4

WORKDIR /code

COPY requirements.txt /code

RUN apt-get update && apt-get install --reinstall build-essential

ADD odbcinst.ini /etc/odbcinst.ini
RUN apt-get update
RUN apt-get install -y tdsodbc unixodbc-dev
RUN apt-get install unixodbc -y
RUN apt-get clean -y


RUN apt-get update -y && apt-get install -y gcc curl gnupg build-essential

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /code

CMD [ "python", "main.py" ]