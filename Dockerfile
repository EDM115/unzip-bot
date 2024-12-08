FROM python:3.12-alpine AS build

RUN apk update && \
    apk add --no-cache \
        bash \
        curl \
        g++ \
        gcc \
        libffi-dev \
        make \
        musl-dev && \
    python -m venv /venv

SHELL ["/bin/bash", "-c"]

ENV PATH="/venv/bin:$PATH"

WORKDIR /tmp

COPY requirements.txt /tmp/requirements.txt
COPY install_unrar.sh /tmp/install_unrar.sh

RUN pip install -U pip setuptools wheel && \
    pip install -r /tmp/requirements.txt && \
    /tmp/install_unrar.sh

FROM python:3.12-alpine

ARG VERSION="7.1.4a"

LABEL org.opencontainers.image.authors="EDM115 <unzip@edm115.dev>"
LABEL org.opencontainers.image.base.name="python:3.12-alpine"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.source="https://github.com/EDM115/unzip-bot.git"
LABEL org.opencontainers.image.title="unzip-bot"
LABEL org.opencontainers.image.url="https://github.com/EDM115/unzip-bot"
LABEL org.opencontainers.image.version=${VERSION}

RUN apk update && \
    apk add --no-cache \
        bash \
        cgroup-tools \
        cpulimit \
        curl \
        ffmpeg \
        git \
        tar \
        tzdata \
        util-linux \
        zstd && \
    apk add --no-cache 7zip --repository=https://dl-cdn.alpinelinux.org/alpine/edge/main && \
    python -m venv /venv && \
    ln -sf /usr/share/zoneinfo/Europe/Paris /etc/localtime && \
    mkdir /app

SHELL ["/bin/bash", "-c"]

ENV PATH="/venv/bin:$PATH"
ENV TZ=Europe/Paris

WORKDIR /app

COPY --from=build /venv /venv
COPY --from=build /usr/local/bin/unrar /tmp/unrar

RUN git clone -b v7 --single-branch https://github.com/EDM115/unzip-bot.git /app && \
    install -m 755 /tmp/unrar /usr/local/bin && \
    rm -rf /tmp/unrar

COPY .env /app/.env

ENTRYPOINT ["/bin/bash", "/app/start.sh"]
