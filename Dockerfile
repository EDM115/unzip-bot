FROM archlinux:latest

RUN pacman -Syyu --noconfirm
RUN pacman -S --noconfirm python-pip zstd p7zip gcc git
RUN pip3 install -U pip
RUN mkdir /app/
WORKDIR /app/
# COPY . /app/
RUN git clone https://github.com/EDM115/unzip-bot.git /app/
RUN pip3 install -U setuptools wheel
RUN pip3 install -U -r requirements.txt
CMD bash start.sh
