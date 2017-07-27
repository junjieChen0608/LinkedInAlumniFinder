FROM python:3.5

RUN mkdir /app
WORKDIR /app

COPY . /app
RUN pip3 install -r requirements.txt