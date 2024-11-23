<div align="center">

# unzip-bot
## A Telegram bot to extract various types of archives

<img src="https://telegra.ph/file/d4ba24682e030fc58613f.jpg" alt="unzip-bot" width="200" height="200">

[![Code style : black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) [![DeepSource](https://app.deepsource.com/gh/EDM115/unzip-bot.svg/?label=active+issues&show_trend=true&token=17SfwVx77dbrFlixtGdQsQNh)](https://app.deepsource.com/gh/EDM115/unzip-bot/?ref=repository-badge)

[![unzip-bot analytics](https://repobeats.axiom.co/api/embed/5c857b55b42dd8235388093858b74341f6c679ac.svg)](https://github.com/EDM115/unzip-bot/pulse)

</div>

## Working bot :smiling_face_with_three_hearts:
[@unzip_edm115bot](https://t.me/unzip_edm115bot)  
More info : [edm115.dev/unzip](https://edm115.dev/unzip)

## Features :eyes:
### User side
- Extract all formats of archives like `rar`, `zip`, `7z`, `tar.gz`, …
- Supports password protected archives
- Able to process splitted archives (`.001`, `.partX.rar`, …)
- Download files from links
- Rename and set custom thumbnail for files
- Uploads files as documents or media
- Can report issues directly

### Admin side
- Broadcast messages to all users or specific ones
- Ban/unban users from using your bot
- Get realtime stats of the bot usage, along an API
- Ability to set sudo users
- Restart simply the bot and pull updates in one command
- Can eval and exec code directly from Telegram
- Send logs in a custom channel/group + retrieve logs from the bot  
And much more :fire: Dive into the code to find out :hand_over_mouth:

## Config vars :book:
- `APP_ID` - Your APP ID. Get it from [my.telegram.org](my.telegram.org)
- `API_HASH` - Your API_HASH. Get it from [my.telegram.org](my.telegram.org)
- `BOT_OWNER` - Your Telegram Account ID. Get it from [@MissRose_bot](https://t.me/MissRose_bot) (Start the bot and send `/info` command).
- `BOT_TOKEN` - Bot Token of Your Telegram Bot. Get it from [@BotFather](https://t.me/BotFather)
- `MONGODB_DBNAME` - *(optional)* A custom name for the MongoDB database, useful if you deploy multiple instances of the bot on the same account. Defaults to `Unzipper_Bot`
- `MONGODB_URL` - Your MongoDB URL ([**tutorial here**](./CreateMongoDB.md))
- `LOGS_CHANNEL` - Make a private channel and get its ID (search on Google if you don't know how to do). Using a group works as well, just add [`Rose`](https://t.me/MissRose_bot?startgroup=startbot), then send `/id` (In both cases, **make sure to add your bot to the channel/group as an admin !**)

## Commands :writing_hand:
Copy-paste those to BotFather when he asks you for them
```text
commands - Get commands list
mode - Upload as Doc 📄 / Media 📺
addthumb - Add custom thumbnail
delthumb - Remove your thumbnail
stats - Know if bot is overused
clean - Cancel ongoing process
help - In case you need 😭
```

## Deploy :construction:
Deploying is easy :smiling_face_with_three_hearts: You can deploy this bot in Heroku or in a VPS :heart:  
**Star :star2: Fork :fork_and_knife: and Deploy :outbox_tray:**

> [!NOTE]  
> We are using Arch Linux as a base image. But why :thinking:  
> Because Arch's p7zip package is the only maintained version of the [original p7zip](http://p7zip.sourceforge.net/) package with some additional features  
> **EDIT** : We might switch to Alpine Linux in the future, I still have to compare the commits done on the p7zip package

#### The lazy way
[![Deploy me :pleading_face:](https://www.herokucdn.com/deploy/button.svg)](https://www.heroku.com/deploy?template=https://github.com/EDM115/unzip-bot/tree/v7)  
(if you're in a fork, make sure to replace the template URL with your repo's one, also replace the URL in the Dockerfile)

#### The easy way
- Install [Docker](https://www.docker.com/) then restart your computer (if on Windows)
```bash
git clone https://github.com/EDM115/unzip-bot.git && cd unzip-bot
nano .env
docker build -t edm115/unzip-bot .
```
- Open Docker Desktop, go on the Images tab, click on the Run button
- On Optional settings, fill the env variables

#### The legacy way
```bash
git clone https://github.com/EDM115/unzip-bot.git && cd unzip-bot
pip3 install -r requirements.txt
```
- Install required dependencies  
  Arch Linux : `sudo pacman -S p7zip`  
  Ubuntu/Debian : `sudo apt-get install p7zip-full p7zip-rar`
- Edit `.env` with your own values
```bash
chmod +x start.sh && ./start.sh
```

**DONE :partying_face: enjoy the bot !** Be sure to follow me on [Github](https://github.com/EDM115) and Star :star2: this repo to show some support :pleading_face:

## How to build after changes ?
#### Trust GitHub Actions
- Add new Actions secrets to the repo :
  - `DOCKER_USERNAME` : all in lowercase
  - `DOCKER_TOKEN` : one with all rights, here : https://hub.docker.com/settings/security
- Go in Actions tab, 2 workflows are here for ya :
  - `Build Docker Image` : Check if it builds without errors
  - `Publish Docker Image` : Rebuild && publish

#### Do it manually
- Go in the repo's folder
```bash
docker build --no-cache -t edm115/unzip-bot .
docker run -d -v downloaded-volume:/app/Downloaded -v thumbnails-volume:/app/Thumbnails --env-file ./.env --network host --name unzip-bot-container edm115/unzip-bot
docker start unzip-bot-container
# if you want to check something
docker exec -it unzip-bot-container sh
docker logs unzip-bot-container
# once you're done
docker stop unzip-bot-container
```
- If you wanna publish :
```bash
docker tag edm115/unzip-bot edm115/unzip-bot:latest
```
*(replace `edm115` with your docker hub username, `unzip-bot` with the repo's name and `latest` whith whatever you want)*
```bash
docker login
```
*login and don't mind the errors*
```bash
docker push edm115/unzip-bot:latest
```
*(same, replace accordingly)*

## Found a bug :bug:
If you found a bug in this bot please open an [issue](https://github.com/EDM115/unzip-bot/issues) or report it on Telegram : [@EDM115](https://t.me/EDM115)  
Same if you have any feature request :wink:

## License & Copyright :cop:
Copyright (c) 2022 - 2024 EDM115  
  
This unzip-bot repository is licensed under the [MIT License](https://github.com/EDM115/unzip-bot/blob/master/LICENSE)  
Enjoy copying and modifying, but always mention me  
  
• Inspired by Itz-fork/Nexa's work, but with additional features and bug fixes.  
This is a maintained repo of the [original](https://github.com/Itz-fork/Unzipper-Bot), props to him for the OG code
