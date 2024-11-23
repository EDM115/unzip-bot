#!/bin/bash

echo "
🔥 unzip-bot 🔥

Copyright (c) 2022 - 2024 EDM115

--> Join @EDM115bots on Telegram
--> Follow EDM115 on Github
"

if [ -f .env ]; then
  if grep -qE '^[^#]*=\s*("|'\''?)\s*\1\s*$' .env; then
    echo "Some required vars are empty, please fill them unless you're filling them somewhere else (ex : Heroku, Docker Desktop)"
  else
    export "$(grep -v '^#' .env | xargs)"
  fi
fi

export TZ="Europe/Paris"

echo "Debug environment variables : "
printenv

exec python -m unzipbot
