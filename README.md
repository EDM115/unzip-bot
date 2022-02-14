<h1 align="center">》 Unzipper Bot 《</h1>

<p align="center">
  A Telegram Bot to Extract Various Types Of Archives
</p>

</br></br>


## Features

- Extract various types of archives like `rar`, `zip`, `tar`, `7z`, `tar.xz` etc.
- Password support for extracting
- Extract archives from direct links
- Broadcast Messages to users
- Ban / Unban users from using your bot
- Send logs in a private channel

And Some other features 🔥!


## Configs 📖

- `APP_ID` - Your APP ID. Get it from [my.telegram.org](my.telegram.org)
- `API_HASH` - Your API_HASH. Get it from [my.telegram.org](my.telegram.org)
- `BOT_OWNER` - Your Telegram Account ID. Get it from [@MissRose_bot](https://t.me/MissRose_bot) (Start the bot and send <samp>/info</samp> command).
- `BOT_TOKEN` - Bot Token of Your Telegram Bot. Get it from [@BotFather](https://t.me/BotFather)
- `MONGODB_URL` - Your MongoDB url, Tutorial [here](https://www.youtube.com/watch?v=0aYrJTfYBHU)
- `LOGS_CHANNEL` - Make a private channel and forward a message from that channel to [@ChannelidHEXbot](https://t.me/ChannelidHEXbot) to Get this. (Make sure to add Your bot to the channel as an admin)

</br>


## Deploy 👀

Deploying is easy 🤫! You can deploy this bot in Heroku or in a VPS ♥️! **Star 🌟 Fork 🍴 and Deploy**

> Note ⚠️
> This branch is using arch linux.
> 
> But Why 🤔? Cuz arch's p7zip package is the only maintained version of [original p7zip](http://p7zip.sourceforge.net/) package with some additional features

#### With Heroku

<a href="https://www.heroku.com/deploy?template=https://github.com/Itz-fork/Unzipper-Bot/tree/arch">
  <img src="https://www.herokucdn.com/deploy/button.svg">
</a>

---

#### Self-Hosting

```bash
git clone -b arch https://github.com/Itz-fork/Unzipper-Bot.git
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

**DONE 🥳, Enjoy The Bot! Be sure to Follow Me on [Github](https://github.com/Itz-fork) and Star 🌟 this repo to Show some support 😍!**

</br>


## Found a bug 🐞?

If you found a bug in this bot please open an [issue](https://github.com/Itz-fork/Unzipper-Bot/issues) or report it at the [Support Group](#support).

</br>


## Support 💙

<a href="https://t.me/NexaBotsUpdates">
  <img src="https://img.shields.io/badge/Updates_Channel-0a0a0a?style=for-the-badge&logo=telegram&logoColor=white">
</a>
<a href="https://t.me/Nexa_bots">
  <img src="https://img.shields.io/badge/Support_Group-0a0a0a?style=for-the-badge&logo=telegram&logoColor=white">
</a>

</br>


## License & Copyright 👮

```
Copyright (c) 2021 Itz-fork

This Unzipper-Bot repository is licensed under GPLv3 License (https://github.com/Itz-fork/Unzipper-Bot/blob/master/LICENSE)
Copying or Modifying Any Part of the code without permission is strictly prohibited
```
