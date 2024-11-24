#!/bin/bash

echo "
🔥 unzip-bot 🔥

Copyright (c) 2022 - 2024 EDM115
MIT License

--> Join @EDM115bots on Telegram
--> Follow EDM115 on Github
"

if [ -f .env ] && [[ ! "$DYNO" =~ ^worker.* ]]; then
  if grep -qE '^[^#]*=\s*("|'\''?)\s*\1\s*$' .env; then
    echo "Some required vars are empty, please fill them unless you're filling them somewhere else (ex : Heroku, Docker Desktop)"
  else
    while IFS='=' read -r key value; do
      if [[ ! $key =~ ^# && -n $key ]]; then
        export "$key=$value"
      fi
    done < .env
  fi
fi

export TZ="Europe/Paris"

exec python -m unzipbot
