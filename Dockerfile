FROM archlinux:latest

RUN pacman -Syyu --noconfirm && \
    pacman -S --noconfirm ffmpeg gcc git p7zip python-pip tzdata zstd && \
    python3 -m venv /venv && \
    pacman -Scc --noconfirm && \
    ln -sf /usr/share/zoneinfo/Europe/Paris /etc/localtime
ENV PATH="/venv/bin:$PATH"
ENV TZ=Europe/Paris
RUN pip3 install -U pip setuptools wheel && \
    mkdir /app
WORKDIR /app
RUN git clone https://github.com/EDM115/unzip-bot.git /app && \
    pip3 install -U -r requirements.txt
COPY .env /app/.env
CMD ["/bin/bash", "start.sh"]
