<div align="center">
  
# Unarchiver Bot
## A Telegram bot to extract various types of archives
![Unzip logo](https://telegra.ph/file/426207477776ffa00519f.png)
</div>
</br></br>

## Demo π₯°
[@unzip_edm115bot](https://t.me/unzip_edm115bot)  
β οΈ From 00h to 08h UTC+1, the [beta](https://github.com/EDM115/unzip-bot/tree/beta) version is running. Try it at your own risksβ¦  
  
## Features π
- Extract various types of archives like `rar`, `zip`, `tar`, `7z`, `tar.xz`, β¦
- Supports password protected archives
- Extract archives from direct links
- Broadcast messages to users
- Ban / Unban users from using your bot
- Send logs in a private channel/group
- Can run only one extract per user at a time
- Download speed : 4-12 Mb/s, can be even more if you're lucky
- Upload speed : 15-25 Mb/s, unexpectedly
- Fast to answer and process tasks
- And some other features π₯ Dive into the code to find them π€­
  
## Simple version π
I made a special version if you only want to use it personally. Works smoother but with less features.  
[**π Try it here π**](https://github.com/EDM115/unzip-bot/tree/personal_only)

## Bugs to fix and features to add π  
[**Check the beta branch to find them. They normally also are on the master one**](https://github.com/EDM115/unzip-bot/blob/beta/README.md#bugs-to-fix-and-features-to-add-)  
Those are things that are fixed/added regarding to [`original repo`](https://github.com/EDM115/unzip-bot#license--copyright-%EF%B8%8F)
  
## Config vars π
- `APP_ID` - Your APP ID. Get it from [my.telegram.org](my.telegram.org)
- `API_HASH` - Your API_HASH. Get it from [my.telegram.org](my.telegram.org)
- `BOT_OWNER` - Your Telegram Account ID. Get it from [@MissRose_bot](https://t.me/MissRose_bot) (Start the bot and send <samp>/info</samp> command).
- `BOT_TOKEN` - Bot Token of Your Telegram Bot. Get it from [@BotFather](https://t.me/BotFather)
- `MONGODB_URL` - Your MongoDB URL ([**tutorial here**](./CreateMongoDB.md))
- `LOGS_CHANNEL` - Make a private channel and get its ID (search on Google if you don't know how to do). Using a group works as well, just add [`Rose`](https://t.me/MissRose_bot?startgroup=startbot), then send `/id` (In both cases, make sure to add your bot to the channel/group as an admin !)

## Commands βοΈ
Copy-paste those to BotFather when he asks you for them  
```
clean - Remove your archives from my servers π?β»οΈ
mode - Upload things as Doc π or Video πΉ (alias : /setmode)
start - Alive check πͺ Also useful after updates π₯°
```  
Admin only commands (better to not include them)  
```
stats - Get detailed stats about users and server
broadcast - Reply with this to a message to send it at every user
ban - {id of user}
unban - {id of user}
```
  
## Deploy π§
Deploying is easy π₯° You can deploy this bot in Heroku or in a VPS β₯οΈ  
**Star π Fork π΄ and Deploy π€**

> β οΈ Note :
> We are using arch linux. But why π€
> 
> Because archβs p7zip package is the only maintained version of the [original p7zip](http://p7zip.sourceforge.net/) package with some additional features !
---
#### The lazy way 
[![Deploy me π₯Ί](https://www.herokucdn.com/deploy/button.svg)](https://www.heroku.com/deploy?template=https://github.com/EDM115/unzip-bot/tree/master)  
(if you're in a fork, make sure to replace the template URL with your repoβs one)

---
#### The legacy way
```bash
git clone -b master https://github.com/EDM115/unzip-bot.git
cd unzip-bot
pip3 install -r requirements.txt
# Arch linux only β
sudo pacman -S p7zip
# Edit config.py with your own values
bash start.sh
```
---
**DONE π₯³ enjoy the bot !** Be sure to follow me on [Github](https://github.com/EDM115) and Star π this repo to show some support π₯Ί
  
  
## Found a bug π
If you found a bug in this bot please open an [issue](https://github.com/EDM115/unzip-bot/issues) or report it at [me](https://t.me/EDM115)  
Same if you have any feature request βΊοΈ
  
## License & Copyright π?ββοΈ
```
Copyright (c) 2022 EDM115

This Unarchiver Bot repository is licensed under MIT License (https://github.com/EDM115/unzip-bot/blob/master/LICENSE)
Enjoy copying and modifying, but always mention me
```
β’ Inspired by Itz-fork/Nexaβs work, but with additional features and bug fixes. This is a maintained repo of the [original](https://github.com/Itz-fork/Unzipper-Bot)
