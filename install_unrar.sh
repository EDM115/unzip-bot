#!/bin/bash

# unrar build and install script
# origin : https://github.com/linuxserver/docker-sabnzbd/blob/444da02e31823289c4d4ca6ab407442bf6719e94/Dockerfile#L28-L38
# source : https://www.reddit.com/r/AlpineLinux/comments/13p4p5k/comment/jmrdr24/
# get unrar version : https://www.rarlab.com/rar_add.htm
UNRAR_VERSION="7.1.2"

echo "Installing unrar version: ${UNRAR_VERSION}"
mkdir /tmp/unrar
curl -o \
  /tmp/unrar.tar.gz -L \
  "https://www.rarlab.com/rar/unrarsrc-${UNRAR_VERSION}.tar.gz"

tar xf \
  /tmp/unrar.tar.gz -C \
  /tmp/unrar --strip-components=1
cd /tmp/unrar || exit

make
install -v -m755 unrar /usr/local/bin
echo "unrar version: $(unrar -iver) installed successfully"
