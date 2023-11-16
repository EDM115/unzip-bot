FROM archlinux:latest

RUN pacman -Syyu --noconfirm && \
    pacman -S --noconfirm python-pip zstd p7zip git ffmpeg && \
    pacman -Rsu --noconfirm cairo alsa-lib default-cursors fontconfig freetype2 \
    gdk-pixbuf2 giflib gperftools gsm harfbuzz hicolor-icon-theme hidapi imath \
    jack2 lcms2 libass libbluray libbs2b libjpeg-turbo libiec61883 libjxl \
    libopenmpt libpng libpulse librsvg libthai libtheora libtiff libusb libva \
    libvdpau libwebp libxcursor libx11 libxau libxcb libxdamage libxdmcp \
    libxext libxfixes libxft libxrender libxv libxxf86vm mesa mpg123 ocl-icd \
    onevpl openexr openjpeg2 pango pcre2 perl-mailtools perl-error perl-timedate \
    perl pixman portaudio sdl2 speex speexdsp sqlite v4l-utils \
    vid.stab vmaf vulkan-icd-loader wayland xorgproto zimg && \
    pacman -Rnsu $(pacman -Qdtq) && \
    pacman -Scc --noconfirm

RUN python -m venv /venv && \
    . /venv/bin/activate && \
    pip install -U pip setuptools wheel

ENV PATH="/venv/bin:$PATH"

WORKDIR /app

RUN git clone https://github.com/EDM115/unzip-bot.git /app && \
    pip install -U -r requirements.txt

CMD ["bash", "start.sh"]
