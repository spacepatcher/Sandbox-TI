FROM python:3.6.2-alpine3.6

ADD ./app/ /app/Sandbox-TI

WORKDIR /app/Sandbox-TI

RUN apk update \
    && apk upgrade \
    && apk add git \
    && pip install --no-cache-dir -r requirements.txt

ENTRYPOINT python scheduler.py
