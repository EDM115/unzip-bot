FROM archlinux:latest

RUN pacman -Syyu --noconfirm && \
    pacman -S --noconfirm python-pip zstd p7zip gcc git ffmpeg && \
    python -m venv /venv
ENV PATH="/venv/bin:$PATH"
RUN pip install -U pip setuptools wheel && \
    mkdir /app && \
    pacman -Scc --noconfirm
WORKDIR /app
RUN git clone https://github.com/EDM115/unzip-bot.git /app
COPY requirements.txt /app/requirements.txt
RUN pip install -U -r requirements.txt
CMD ["bash", "start.sh"]
