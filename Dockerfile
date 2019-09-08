FROM python:3.7-alpine

RUN mkdir -p /code
WORKDIR /code
ENV SHELL=/bin/sh

COPY . /code

RUN apk add --no-cache git
RUN apk add build-base libffi-dev
RUN apk add autoconf automake g++ make --no-cache

RUN pip install -U pip && pip install --no-cache-dir invoke && invoke requirements && invoke clean

CMD ["invoke", "server"]
