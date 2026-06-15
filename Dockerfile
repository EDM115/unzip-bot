FROM python:3.12-alpine

ENV UV_INSTALL_DIR="/uv"
ENV TERM=xterm
ARG VERSION="7.4.0"

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
        g++ \
        gcc \
        git \
        jq \
        libffi-dev \
        make \
        musl-dev \
        ncurses \
        tar \
        tzdata \
        util-linux \
        zstd && \
    apk add --no-cache dos2unix --repository=https://dl-cdn.alpinelinux.org/alpine/v3.21/community && \
    apk add --no-cache 7zip --repository=https://dl-cdn.alpinelinux.org/alpine/edge/main && \
    curl -LsSf https://astral.sh/uv/install.sh | sh && \
    ln -sf /usr/share/zoneinfo/Europe/Paris /etc/localtime

SHELL ["/bin/bash", "-c"]

ENV PATH="$UV_INSTALL_DIR:/app/.venv/bin:$PATH"
ENV TZ=Europe/Paris

WORKDIR /app

RUN git clone -b v7-rework-part-1 https://github.com/EDM115/unzip-bot.git /app && \
    uv sync --no-cache --locked && \
    curl -LsSf https://api.github.com/repos/EDM115/unrar-alpine/releases/latest \
        | jq -r '.assets[] | select(.name == "unrar") | .id' \
        | xargs -I {} curl -LsSf https://api.github.com/repos/EDM115/unrar-alpine/releases/assets/{} \
        | jq -r '.browser_download_url' \
        | xargs -I {} curl -Lsf {} -o /tmp/unrar && \
    install -m 755 /tmp/unrar /usr/local/bin && \
    rm /tmp/unrar && \
    source /app/.venv/bin/activate && \
    dos2unix /app/start.sh && \
    chmod +x /app/start.sh

ENTRYPOINT ["/bin/bash", "/app/start.sh"]
