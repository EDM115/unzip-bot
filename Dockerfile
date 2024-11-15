FROM python:3.12-alpine

RUN apk update && \
    apk add --no-cache \
        7zip \
        bash \
        curl \
        ffmpeg \
        g++ \
        gcc \
        git \
        libffi-dev \
        make \
        musl-dev \
        tar \
        tzdata \
        zstd && \
    python3 -m venv /venv && \
    ln -sf /usr/share/zoneinfo/Europe/Paris /etc/localtime

ENV PATH="/venv/bin:$PATH"
ENV TZ=Europe/Paris

RUN pip install -U pip setuptools wheel && \
    mkdir /app

WORKDIR /app

RUN git clone -b v7 --single-branch https://github.com/EDM115/unzip-bot.git /app && \
    pip install -U -r requirements.txt && \
    ./install_unrar.sh

COPY .env /app/.env

CMD ["/bin/bash", "start.sh"]
