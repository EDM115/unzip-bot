#!/bin/bash
echo "
🔥 Unzip Bot 🔥

Copyright (c) 2022 - 2024 EDM115

--> Join @EDM115bots on Telegram
--> Follow EDM115 on Github
"
if grep -qE '^[^#]*=\s*("|'\''?)\s*\1\s*$' .env; then
  echo "Some required vars are empty, please fill them unless you're filling them somewhere else (ex : Heroku, Docker Desktop)"
else
  source .env
fi
export TZ="Europe/Paris"
python3 -m unzipper
