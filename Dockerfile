FROM archlinux:latest

RUN pacman -Syyu --noconfirm
RUN pacman -S --noconfirm python-pip zstd p7zip gcc git ffmpeg
RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"
RUN pip install -U pip setuptools wheel
RUN mkdir /app/
WORKDIR /app/
# COPY . /app/
RUN git clone https://github.com/EDM115/unzip-bot.git /app/
COPY requirements.txt /app/requirements.txt
RUN pip install -U -r requirements.txt
CMD bash start.sh