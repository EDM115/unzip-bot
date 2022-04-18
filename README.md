<h1 align="center">Unarchiver Bot</h1>

<p align="center">
  A Telegram bot to extract various types of archives
</p>

<img align="center" src="https://telegra.ph/file/426207477776ffa00519f.png"/>
</br></br>


## Features 👀

- Extract various types of archives like `rar`, `zip`, `tar`, `7z`, `tar.xz`, …
- Supports password protected archives
- Extract archives from direct links
- Broadcast messages to users
- Ban / Unban users from using your bot
- Send logs in a private channel/group

And some other features 🔥 Dive into the code to find them 🤭


## Config vars 📖

- `APP_ID` - Your APP ID. Get it from [my.telegram.org](my.telegram.org)
- `API_HASH` - Your API_HASH. Get it from [my.telegram.org](my.telegram.org)
- `BOT_OWNER` - Your Telegram Account ID. Get it from [@MissRose_bot](https://t.me/MissRose_bot) (Start the bot and send <samp>/info</samp> command).
- `BOT_TOKEN` - Bot Token of Your Telegram Bot. Get it from [@BotFather](https://t.me/BotFather)
- `MONGODB_URL` - Your MongoDB URL, Tutorial [here](https://www.youtube.com/watch?v=0aYrJTfYBHU)
- `LOGS_CHANNEL` - Make a private channel and get its ID (search on Google if you don't know how to do). Using a group works as well, just add [`Rose`](https://t.me/MissRose_bot?groupstart=startbot), then send `/id` (In both cases, make sure to add your bot to the channel/group as an admin !)

</br>


## Deploy 🚧

Deploying is easy 🥰 You can deploy this bot in Heroku or in a VPS ♥️  
**Star 🌟 Fork 🍴 and Deploy 📤**

> ⚠️ Note :
> We are using arch linux
> But why 🤔 Because arch's p7zip package is the only maintained version of [original p7zip](http://p7zip.sourceforge.net/) package with some additional features !

#### With Heroku

<a href="https://www.heroku.com/deploy?template=https://github.com/EDM115/unzip-bot/tree/master">
  <img src="https://www.herokucdn.com/deploy/button.svg">
</a> (if you're in a fork, make sure to replace the template URL with your repo’s one)

---

#### Self-Hosting

```bash
git clone -b arch https://github.com/EDM115/unzip-bot.git
cd Unzipper-Bot
pip3 install -r requirements.txt

# Arch linux only
sudo pacman -S p7zip
```

<h4 align="center">Edit config.py with your own values</h4>

```bash
bash start.sh
```

---

**DONE 🥳 enjoy the bot ! Be sure to follow me on [Github](https://github.com/EDM115) and Star 🌟 this repo to show some support 🥺**

</br>


## Found a bug 🐞

If you found a bug in this bot please open an [issue](https://github.com/EDM115/unzip-bot/issues) or report it at [me](https://t.me/EDM115)  
Same if you have any feature request ☺️

</br>


## License & Copyright 👮

```
Copyright (c) 2022 EDM115

This Unzipper-Bot repository is licensed under GPLv3 License (https://github.com/EDM115/unzip-bot/blob/master/LICENSE)
Copying or Modifying Any Part of the code without permission is strictly prohibited
```

• Inspired by Itz-fork/Nexa’s work, but with additional features and bug fixes. This is a maintained repo of the [original](https://github.com/Itz-fork/Unzipper-Bot)
