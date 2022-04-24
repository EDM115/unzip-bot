<h1 align="center">Unarchiver Bot</h1>

<p align="center">A Telegram bot to extract various types of archives</p>

<img align="center" src="https://telegra.ph/file/426207477776ffa00519f.png"/>
</br></br>

## Demo 🥰

[@unzip_edm115bot](https://t.me/unzip_edm115bot)  
⚠️ From 00h to 08h UTC+1, the [beta](https://github.com/EDM115/unzip-bot/tree/beta) version is running. Try it at your own risks…  
  
## Features 👀

- Extract various types of archives like `rar`, `zip`, `tar`, `7z`, `tar.xz`, …
- Supports password protected archives
- Extract archives from direct links
- Broadcast messages to users
- Ban / Unban users from using your bot
- Send logs in a private channel/group
- And some other features 🔥 Dive into the code to find them 🤭
  
## Bugs to fix and additional features to add 💀  
  
- [ ] The ETA isn't accurate
- [x] ~~Download speed stays constant, depending of what we have at begining. If the download started at 3 Mb/s, it will stay like that through all the process and can't evolve~~ **Seems to have been fixed**
- [ ] While this 👆 is okay, I notice some times where bot is very slow (10-40s to process buttons, DL speed around 200 kB/s…
- [ ] Unzipping normally a password protected archive makes crash the bot 😭
- [ ] [Reply markup error](https://github.com/EDM115/unzip-bot/issues/2)
- [ ] Adding file name in description while uploading
- [ ] Adding a `/db` command that returns a list of all users + banned ones
- [ ] ~~Looks like some "blank" users are added to the db, including a banned one~~ *Actually, the banned db can exist only if at least 1 value is inside. So, since owner have all rights, his ID can be added into it, the owner status will bypass it. But I noticed also other banned users while no `/ban` command were done. Investigating on this…*
- [ ] Add a translation (start a CrowdIn dude)
- [ ] ~~Some profile links doesn't work~~ **Private ones. But maybe I can force it…**
- [ ] Get informations with smth like `/user {id}`, that returns his state (banned or not) + lastly uploaded files (5 last with link to channel/group message) + how many files he sent + size of all of them. The user could also get those infos with a `/me` command
- [ ] Add a `/dbdive` that returns an url where we can visualize the db online
- [ ] Add status of extraction in logs (uploaded, started, extracted, failed (+ error), what is the password, …)
- [ ] Add more things to `/stats` like average speed, …
- [ ] Add cancel process button for downloads and an emergency `/redbutton` one
- [ ] Add an emergency `/restart` command that can be run **even** if the bot hanged up
- [ ] Add permathumb support `/addthumb` `/delthumb`
- [ ] Auto use `/clean` when a task failed
- [ ] Keep the archives 5 hours in server just in case someone resend the same (no download twice)
- [ ] Add a `/cleanall` for forcing the server reset and freeing space
  
## Properties 👋  
- [x] Can run only one extract per user at a time
- [x] Download speed : 2-12 Mb/s, can be even more if you're lucky
- [x] Upload speed : 5-20 Mb/s, unexpectedly
- [x] Fast to answer and process tasks
  
## Config vars 📖

- `APP_ID` - Your APP ID. Get it from [my.telegram.org](my.telegram.org)
- `API_HASH` - Your API_HASH. Get it from [my.telegram.org](my.telegram.org)
- `BOT_OWNER` - Your Telegram Account ID. Get it from [@MissRose_bot](https://t.me/MissRose_bot) (Start the bot and send <samp>/info</samp> command).
- `BOT_TOKEN` - Bot Token of Your Telegram Bot. Get it from [@BotFather](https://t.me/BotFather)
- `MONGODB_URL` - Your MongoDB URL, Tutorial [here](https://www.youtube.com/watch?v=0aYrJTfYBHU)
- `LOGS_CHANNEL` - Make a private channel and get its ID (search on Google if you don't know how to do). Using a group works as well, just add [`Rose`](https://t.me/MissRose_bot?startgroup=startbot), then send `/id` (In both cases, make sure to add your bot to the channel/group as an admin !)

## Commands ✍️

Copy-paste those to BotFather when he asks you for them  
```
clean - Remove your archives from my servers 🚮♻️
mode - Upload things as Doc 📄 or Video 📹 (alias : /setmode)
start - Alive check 😪 Also useful after updates 🥰
```  
Admin only commands (better to not include them)  
```
stats - Get detailed stats about users and server
broadcast - Reply with this to a message to send it at every user
ban - {id of user}
unban - {id of user}
```

</br>

## Deploy 🚧

Deploying is easy 🥰 You can deploy this bot in Heroku or in a VPS ♥️  
**Star 🌟 Fork 🍴 and Deploy 📤**

> ⚠️ Note :
> We are using arch linux
> But why 🤔 Because arch’s p7zip package is the only maintained version of [original p7zip](http://p7zip.sourceforge.net/) package with some additional features !

#### The lazy way

<a href="https://www.heroku.com/deploy?template=https://github.com/EDM115/unzip-bot/tree/master"><img src="https://www.herokucdn.com/deploy/button.svg"></a>  
(if you're in a fork, make sure to replace the template URL with your repo’s one)

---

#### The legacy way

```bash
git clone -b arch https://github.com/EDM115/unzip-bot.git
cd unzip-bot
pip3 install -r requirements.txt
# Arch linux only ↓
sudo pacman -S p7zip
# Edit config.py with your own values
bash start.sh
```

---

**DONE 🥳 enjoy the bot ! Be sure to follow me on [Github](https://github.com/EDM115) and Star 🌟 this repo to show some support 🥺**

</br>

## Found a bug 🐞

If you found a bug in this bot please open an [issue](https://github.com/EDM115/unzip-bot/issues) or report it at [me](https://t.me/EDM115)  
Same if you have any feature request ☺️

</br>

## License & Copyright 👮‍♀️

```
Copyright (c) 2022 EDM115

This Unarchiver Bot repository is licensed under MIT License (https://github.com/EDM115/unzip-bot/blob/master/LICENSE)
Enjoy copying and modifying, but always mention me
```

• Inspired by Itz-fork/Nexa’s work, but with additional features and bug fixes. This is a maintained repo of the [original](https://github.com/Itz-fork/Unzipper-Bot)
