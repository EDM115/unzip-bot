<div align="center">

# Unarchiver Bot **BETA**

## A Telegram bot to extract various types of archives

![Unzip logo](https://telegra.ph/file/426207477776ffa00519f.png)

<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
[![DeepSource](https://deepsource.io/gh/EDM115/unzip-bot.svg/?label=active+issues&show_trend=true&token=17SfwVx77dbrFlixtGdQsQNh)](https://deepsource.io/gh/EDM115/unzip-bot/?ref=repository-badge)

</div>

## Demo 🥰

[@unzip_edm115bot](https://t.me/unzip_edm115bot)
⚠️ From 22h to 06h UTC+1, this beta version is running. Try it at your own risks…

## **THIS IS BETA BRANCH, DON'T BE MAD AT ME IF IT'S BUGGY 😞**

## Important note : it may no longer be deployable. More informations here : https://blog.heroku.com/next-chapter

## WORKAROUNDS (bugs to fix and features to add) 💀

- [ ] The ETA isn't accurate
- [x] Adding a `/db` command that returns a list of all users + banned ones **WILL BE IMPROVED**
- [x] Add a translation (start a CrowdIn dude) [![Crowdin](https://badges.crowdin.net/unzip-bot-edm115/localized.svg)](https://crowdin.com/project/unzip-bot-edm115)
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

## Things to work with on v5 :

Check [issue #38](https://github.com/EDM115/unzip-bot/issues/38)

### Possible v6 ...?

- [ ] Web interface
- [ ] Match with nextgenleech
- [ ] yt-dlp included. because why not
- [ ] Integration with upcomming ARCHIVER BOT 👀
- [ ] Compatibility with premium accounts (4Gb upload)

## Fixed/added :partying_face:

#### Fixed :

- [x] _Download speed stays constant, depending of what we have at begining. If the download started at 3 Mb/s, it will stay like that through all the process and can't evolve_ Fixed with new PyroGram | **Since the latest update I did, download speed is fastest than ever (8-10 Mb/s) and upload speed is around 20-25 Mb/s**
- [x] _Unzipping normally a password protected archive makes crash the bot 😭_ Fixed here : [1](https://github.com/EDM115/unzip-bot/commit/41adcb26d11fa0df2425e7aa1654c88d5a4b2151), [2](https://github.com/EDM115/unzip-bot/commit/e933acdf3b61ee1cc92a194cb53c491537405c8f), [3](https://github.com/EDM115/unzip-bot/commit/db59780a14cbde2da53e739f62462719a3c95cd4), [4](https://github.com/EDM115/unzip-bot/commit/9ed2bb8621f8fb874912d8d7b103af83075c0202), [5](https://github.com/EDM115/unzip-bot/commit/5d6004aaae3a494b2e2a83b9c980cb3c4b94c731)
- [x] _Looks like some "blank" users are added to the db, including a banned one Actually, the banned db can exist only if at least 1 value is inside. So, since owner have all rights, his ID can be added into it, the owner status will bypass it. But I noticed also other banned users while no `/ban` command were done_ [Fix here](https://github.com/EDM115/unzip-bot/commit/6b69084cd7337453effb7e9015d2c77da83f8d81)
- [x] [_Reply markup error_](https://github.com/EDM115/unzip-bot/issues/2)
- [x] _Some profile links doesn't work_ Fixed with replacing `.` with `_`

#### Added :

- [x] _Adding file name in description while uploading_ [Added here](https://github.com/EDM115/unzip-bot/commit/37e534873baba858583729f27927f42da368ed86)
- [x] _Add a `/cleanall` for forcing the server reset and freeing space_

## Take a look about the [changelog](https://github.com/EDM115/unzip-bot/blob/beta/changelog.md) 😏

[![Deploy me 🥺](https://www.herokucdn.com/deploy/button.svg)](https://www.heroku.com/deploy?template=https://github.com/EDM115/unzip-bot/tree/beta)
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template/ENIia-?referralCode=EDM115)

## Found a bug 🐞

If you found a bug in this beta version please open an [issue](https://github.com/EDM115/unzip-bot/issues) or report it at [me](https://t.me/EDM115)
Same if you have any feature request ☺️
