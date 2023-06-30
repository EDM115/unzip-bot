<div align="center">
  
# Unarchiver Bot

## A Telegram bot to extract various types of archives

![Unzip logo](https://telegra.ph/file/d4ba24682e030fc58613f.jpg)

<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
[![DeepSource](https://deepsource.io/gh/EDM115/unzip-bot.svg/?label=active+issues&show_trend=true&token=17SfwVx77dbrFlixtGdQsQNh)](https://deepsource.io/gh/EDM115/unzip-bot/?ref=repository-badge)

</div>

</br></br>

## Working bot 🥰
[@unzip_edm115bot](https://t.me/unzip_edm115bot)  
  
## Features 👀
- Extract all format of archives like `rar`, `zip`, `tar`, `7z`, `tar.xz`, …
- Supports password protected archives
- Extract archives from direct links
- Broadcast messages to users
- Ban / Unban users from using your bot
- Send logs in a private channel/group
- Can run only one extract per user at a time
- Fast to answer and process tasks
- Thumbnail can be set
- Problems can be directly reported
- Can send a message to a specific user
- Get infos about users
- And some other features 🔥 Dive into the code to find them 🤭
  
  
## Config vars 📖
- `APP_ID` - Your APP ID. Get it from [my.telegram.org](my.telegram.org)
- `API_HASH` - Your API_HASH. Get it from [my.telegram.org](my.telegram.org)
- `BOT_OWNER` - Your Telegram Account ID. Get it from [@MissRose_bot](https://t.me/MissRose_bot) (Start the bot and send <samp>/info</samp> command).
- `BOT_TOKEN` - Bot Token of Your Telegram Bot. Get it from [@BotFather](https://t.me/BotFather)
- `MONGODB_URL` - Your MongoDB URL ([**tutorial here**](./CreateMongoDB.md))
- `LOGS_CHANNEL` - Make a private channel and get its ID (search on Google if you don't know how to do). Using a group works as well, just add [`Rose`](https://t.me/MissRose_bot?startgroup=startbot), then send `/id` (In both cases, make sure to add your bot to the channel/group as an admin !)

## Commands ✍️
Copy-paste those to BotFather when he asks you for them  
```
commands - Get commands list
mode - Upload as Doc 📄 / Media 📺
addthumb - Add custom thumbnail 
delthumb - Remove your thumbnail 
stats - Know if bot is overused
clean - Cancel on-going process
help - In case you need 😭
```  
  
## Deploy 🚧
Deploying is easy 🥰 You can deploy this bot in Heroku or in a VPS ♥️  
**Star 🌟 Fork 🍴 and Deploy 📤**

> ⚠️ Note :
> We are using arch linux. But why 🤔
> 
> Because arch’s p7zip package is the only maintained version of the [original p7zip](http://p7zip.sourceforge.net/) package with some additional features
---
#### The lazy way 
[![Deploy me 🥺](https://www.herokucdn.com/deploy/button.svg)](https://www.heroku.com/deploy?template=https://github.com/EDM115/unzip-bot)  
(if you're in a fork, make sure to replace the template URL with your repo’s one)

---
#### The easy way
+ Install [Docker](https://www.docker.com/) then restart your computer
+ ```bash
git clone -b master https://github.com/EDM115/unzip-bot.git
cd unzip-bot
docker build -t unzip-bot .
```
+ Open Docker Desktop, go on the Images tab, click on the Run button
+ On Optional settings, fill the env variables

---
#### The legacy way
```bash
git clone -b master https://github.com/EDM115/unzip-bot.git
cd unzip-bot
pip3 install -r requirements.txt
```
+ Arch linux only ↓
`sudo pacman -S p7zip`

##### Edit config.py with your own values
`start.sh`
---
**DONE 🥳 enjoy the bot !** Be sure to follow me on [Github](https://github.com/EDM115) and Star 🌟 this repo to show some support 🥺
  
  
## Found a bug 🐞
If you found a bug in this bot please open an [issue](https://github.com/EDM115/unzip-bot/issues) or report it on Telegram : [@EDM115](https://t.me/EDM115)  
Same if you have any feature request 😉
  
## License & Copyright 👮‍♀️
```
Copyright (c) 2022 - 2023 EDM115

This Unarchiver Bot repository is licensed under MIT License (https://github.com/EDM115/unzip-bot/blob/master/LICENSE)
Enjoy copying and modifying, but always mention me
```
• Inspired by Itz-fork/Nexa’s work, but with additional features and bug fixes. This is a maintained repo of the [original](https://github.com/Itz-fork/Unzipper-Bot)
