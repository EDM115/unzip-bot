ARG UNARC_BUILD_PLATFORM=linux/386
FROM --platform=${UNARC_BUILD_PLATFORM} alpine:3.24 AS unarc-build

RUN apk add --no-cache curl g++ make && \
    curl -Lsf -o /tmp/unarc-src.tar.gz https://github.com/xredor/unarc/archive/adc333d6cdd76d72da254cc80d766fbbcc683c95.tar.gz && \
    echo '028c52abb51229484e4b4a99f641bdc00e00ad1f8d71e336c21caea6c1a8225d  /tmp/unarc-src.tar.gz' | sha256sum -c - && \
    mkdir /tmp/unarc && \
    tar -xzf /tmp/unarc-src.tar.gz -C /tmp/unarc --strip-components=1 && \
    make -C /tmp/unarc -j2 DEFINES='-DFREEARC_UNIX -DFREEARC_INTEL_BYTE_ORDER' UNIX_LINK_FLAGS='-static -lstdc++ -lrt -lpthread -s'

FROM python:3.12-alpine AS build

ENV UV_INSTALL_DIR="/uv"

RUN apk update && \
    apk add --no-cache bash curl g++ gcc gtk+2.0-dev jq libffi-dev make musl-dev unzip && \
    apk add --no-cache --repository=https://dl-cdn.alpinelinux.org/alpine/edge/testing fpc && \
    curl -LsSf https://astral.sh/uv/install.sh | sh

SHELL ["/bin/bash", "-c"]

ENV PATH="$UV_INSTALL_DIR:$PATH"

WORKDIR /tmp

COPY pyproject.toml /tmp/pyproject.toml
COPY uv.lock /tmp/uv.lock

RUN uv sync --no-cache --locked && \
    curl -LsSf https://api.github.com/repos/EDM115/unrar-alpine/releases/latest \
    | jq -r '.assets[] | select(.name == "unrar") | .id' \
    | xargs -I {} curl -LsSf https://api.github.com/repos/EDM115/unrar-alpine/releases/assets/{} \
    | jq -r '.browser_download_url' \
    | xargs -I {} curl -Lsf {} -o /tmp/unrar && \
    install -v -m755 /tmp/unrar /usr/local/bin

RUN curl -Lsf -o /tmp/lazarus.tar.gz 'https://download.lazarus-ide.org/Lazarus%20Zip%20_%20GZip/Lazarus%204.4/lazarus-4.4-0.tar.gz' && \
    echo '190edc7b7a7b18430502c964a45dfdf5418ff16bbcad5c04423b33a09d22cc06  /tmp/lazarus.tar.gz' | sha256sum -c - && \
    curl -Lsf -o /tmp/peazip-src.zip https://github.com/peazip/PeaZip/releases/download/11.4.0/peazip-11.4.0.src.zip && \
    echo 'd406cd13ef02908ad47af085dffed10dc0591b6214c06088df5849e384e325e0  /tmp/peazip-src.zip' | sha256sum -c - && \
    mkdir /tmp/pea-build && \
    tar -xzf /tmp/lazarus.tar.gz -C /tmp/pea-build && \
    unzip -q /tmp/peazip-src.zip -d /tmp/pea-build && \
    make -C /tmp/pea-build/lazarus lazbuild > /tmp/lazbuild.log 2>&1 || { tail -n 40 /tmp/lazbuild.log; exit 1; }

RUN /tmp/pea-build/lazarus/lazbuild --lazarusdir=/tmp/pea-build/lazarus --add-package /tmp/pea-build/peazip-11.4.0.src/dev/metadarkstyle/metadarkstyle.lpk > /tmp/pea-package.log 2>&1 || { tail -n 40 /tmp/pea-package.log; exit 1; }; \
    /tmp/pea-build/lazarus/lazbuild --lazarusdir=/tmp/pea-build/lazarus --widgetset=gtk2 /tmp/pea-build/peazip-11.4.0.src/dev/project_pea.lpi > /tmp/pea-build.log 2>&1 || { tail -n 40 /tmp/pea-build.log; exit 1; }; \
    install -m 755 /tmp/pea-build/peazip-11.4.0.src/dev/pea /usr/local/bin/pea

FROM python:3.12-alpine

ARG TARGETARCH

ENV UV_INSTALL_DIR="/uv"
ARG VERSION="7.4.0"

LABEL org.opencontainers.image.authors="EDM115 <unzip@edm115.dev>"
LABEL org.opencontainers.image.base.name="python:3.12-alpine"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.source="https://github.com/EDM115/unzip-bot.git"
LABEL org.opencontainers.image.title="unzip-bot"
LABEL org.opencontainers.image.url="https://github.com/EDM115/unzip-bot"
LABEL org.opencontainers.image.version=${VERSION}

RUN test "$TARGETARCH" = amd64 && \
    apk add --no-cache bash ca-certificates cgroup-tools coreutils cpulimit curl ffmpeg fontconfig git gtk+2.0 libstdc++ libgcc tar ttf-dejavu tzdata util-linux xauth xvfb xvfb-run zstd && \
    apk add --no-cache 7zip --repository=https://dl-cdn.alpinelinux.org/alpine/edge/main && \
    ln -sf /usr/share/zoneinfo/Europe/Paris /etc/localtime && \
    fc-cache -f

SHELL ["/bin/bash", "-c"]

ENV PATH="$UV_INSTALL_DIR:/venv/bin:$PATH"
ENV TZ=Europe/Paris
ENV HOME=/home/unzipbot

WORKDIR /app

RUN addgroup -S -g 10001 unzipbot && \
    adduser -S -D -u 10001 -G unzipbot -h "$HOME" unzipbot && \
    install -d -o unzipbot -g unzipbot "$HOME" /app /app/Downloaded /app/Thumbnails

COPY --from=build /tmp/.venv /venv
COPY --from=build /uv /uv
COPY --from=build /usr/local/bin/unrar /usr/local/bin/unrar
COPY --from=unarc-build /tmp/unarc/unarc /usr/local/bin/unarc
COPY --from=build /usr/local/bin/pea /usr/local/bin/pea

COPY --chown=unzipbot:unzipbot . /app

USER unzipbot:unzipbot

RUN git init -b v7 && \
    git remote add origin https://github.com/EDM115/unzip-bot.git && \
    git fetch --depth=1 origin v7 && \
    git reset --mixed origin/v7 && \
    git branch --set-upstream-to=origin/v7 v7

ENTRYPOINT ["/bin/bash", "/app/start.sh"]
