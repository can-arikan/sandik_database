FROM python:3.11.3

RUN apt-get update && \
    apt-get install -y build-essential libzbar-dev && \
    apt-get install ffmpeg libsm6 libxext6  -y && \
    apt install libgl1-mesa-glx

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

RUN python manage.py makemigrations

RUN python manage.py migrate