<div align="center">

# Unarchiver Bot
## A Telegram bot to extract various types of archives
![Unzip logo](https://telegra.ph/file/426207477776ffa00519f.png)
</div>
  
  
## Demo 🥰

[@unzip_edm115bot](https://t.me/unzip_edm115bot)  
⚠️ From 22h to 06h UTC+1, this beta version is running. Try it at your own risks…  
  
# **THIS IS BETA BRANCH, DON'T BE MAD AT ME IF IT'S BUGGY 😞**
[![Manual deploy of beta branch](https://github.com/EDM115/unzip-bot/actions/workflows/beta-auto-deploy.yml/badge.svg?branch=beta)](https://github.com/EDM115/unzip-bot/actions/workflows/beta-auto-deploy.yml)  
  
  
## Bugs to fix and features to add 💀  
  
- [ ] The ETA isn't accurate
- [x] Adding a `/db` command that returns a list of all users + banned ones **WILL BE IMPROVED**
- [ ] Add a translation (start a CrowdIn dude) [![Crowdin](https://badges.crowdin.net/unzip-bot-edm115/localized.svg)](https://crowdin.com/project/unzip-bot-edm115)
- [ ] Get informations with smth like `/user {id}`, that returns his state (banned or not) + lastly uploaded files (5 last with link to channel/group message) + how many files he sent + size of all of them. The user could also get those infos with a `/me` command
- [x] Add a `/dbdive` that returns an url where we can visualize the db online **CAN BE IMPROVED**
- [x] Add status of extraction in logs (uploaded, started, extracted, failed (+ error), what is the password, …) **HALF-DONE**
- [ ] Add more things to `/stats` like average speed, …
- [ ] Add cancel process button for downloads and an emergency `/redbutton` one
- [x] Add an emergency `/restart` command that can be run **even** if the bot hanged up
- [x] Add permathumb support `/addthumb` `/delthumb`
- [x] Auto use `/clean` when a task failed **NOT 100% accurate**
- [x] Keep the archives 5 hours in server just in case someone resend the same (no download twice) **Will probably NOT be implemented**
- [ ] Add group support. You add bot to group as admin, then reply to any file with `/extract`. Then you choose where goes the files (group or PM), and drop here do the instructions (pass or no, what to upload, …)
  
## Fixed/added :partying_face:
#### Fixed :
- [x] *Download speed stays constant, depending of what we have at begining. If the download started at 3 Mb/s, it will stay like that through all the process and can't evolve* Fixed with new PyroGram
- [x] *Unzipping normally a password protected archive makes crash the bot 😭* Fixed here : [1](https://github.com/EDM115/unzip-bot/commit/41adcb26d11fa0df2425e7aa1654c88d5a4b2151), [2](https://github.com/EDM115/unzip-bot/commit/e933acdf3b61ee1cc92a194cb53c491537405c8f), [3](https://github.com/EDM115/unzip-bot/commit/db59780a14cbde2da53e739f62462719a3c95cd4), [4](https://github.com/EDM115/unzip-bot/commit/9ed2bb8621f8fb874912d8d7b103af83075c0202), [5](https://github.com/EDM115/unzip-bot/commit/5d6004aaae3a494b2e2a83b9c980cb3c4b94c731)
- [x] *Looks like some "blank" users are added to the db, including a banned one Actually, the banned db can exist only if at least 1 value is inside. So, since owner have all rights, his ID can be added into it, the owner status will bypass it. But I noticed also other banned users while no `/ban` command were done* [Fix here](https://github.com/EDM115/unzip-bot/commit/6b69084cd7337453effb7e9015d2c77da83f8d81)
- [x] [*Reply markup error*](https://github.com/EDM115/unzip-bot/issues/2)
- [x] *Some profile links doesn't work* Fixed with replacing `.` with `_`

#### Added :
- [x] *Adding file name in description while uploading* [Added here](https://github.com/EDM115/unzip-bot/commit/37e534873baba858583729f27927f42da368ed86)
- [x] *Add a `/cleanall` for forcing the server reset and freeing space*

  
[![Deploy me 🥺](https://www.herokucdn.com/deploy/button.svg)](https://www.heroku.com/deploy?template=https://github.com/EDM115/unzip-bot/tree/beta)  
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template/ENIia-?referralCode=EDM115)  
  
## Found a bug 🐞

If you found a bug in this beta version please open an [issue](https://github.com/EDM115/unzip-bot/issues) or report it at [me](https://t.me/EDM115)  
Same if you have any feature request ☺️
