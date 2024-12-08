<div align="center">
<img src="https://telegra.ph/file/d4ba24682e030fc58613f.jpg" alt="unzip-bot" width="200" height="200">

# unzip-bot • Changelog
## You will find here all the changes made with each version, in antichronological order

</div>

> [!NOTE]  
> Updates versions follow semantic versioning (`vX.Y.Z`), where `X` stands for a major change and a lot of new features, `Y` for some new features and bug fixes, `Z` for testing stuff and undebugged things

---

### v7.1.4a **[LATEST ALPHA RELEASE]**
- Try the KurimuzonAkuma fork of `pyrogram`
- Bump `unrar` and `python` versions
- Correctly display the unrar version on the build script
- Already present thumbnails aren't downloaded on a start (useful when they are stored in a volume)

### v7.1.3a
- Cleans the download dir on startup (especially helps when the bot is running with a volume attached)
- Fixed issues with the lockfile that prevented the bot from starting
- Removed an infinite loop that caused the bot to never go idle

### v7.1.2a
- Creates a lock file on start
- Deletes it in case of errors/shutting down
- Restricts users from processing archives when the bot haven't started yet

### v7.1.1a
- Fixed `/exec` not being able to run properly
- `/restart` now sends correctly the logs
- Revert switch to `pyroblack`
- Limit CPU usage too using `cpulimit`
  - Gets maxed at 80% of the current amount of cores for shell tasks
  - Ensures enough room is left to the bot process

### v7.1.0a
- Stop using `return await` in async functions
- apply my very own code style on top of black
  - manually done yet
  - inspired by my heavily modified ESLint Stylistic config (https://github.com/EDM115/website/blob/master/eslint.config.js)
  - simply spaces out return, try, if, with, ... blocks to determine easier the branches that the program may take
- Fixed a crash in the previous version
- Use 80% of the available RAM on Heroku too instead of 100%
- Shell commands are no longer using `shlex.join` to avoid several issues with path interpretation
- Removal of duplicate logic
- Video duration is properly parsed now, and the logic to catch non generated thumbnail is simplified
- Migrate from `pyrogram` to `pyroblack`

### v7.0.3a
- Moved `ERROR_MSGS` strings to a better place
- Private functions have a more coherent naming
- Uses `asyncio.create_subprocess_shell()` instead of the hackish way that was present before
- Uses `shlex` to sanitize user input for shell commands (file paths and archive passwords)
- Fixed an oversight where `ffmpeg` commands were thread blocking

### v7.0.2a
- Bumped `aiohttp`
- The bot now stops properly when sent SIGKILL
- Fixed an issue with formatting of strings
- Implemented a momory limit on ran commands to avoid R14 and R15 errors on Heroku (first using `resource` then `ulimit`)
- `/restart` and `/gitpull` now sends logs to the logs channel
- Shell commands now uses `bash` instead of `sh`
- Set a manual limit of RAM in Heroku (512 MB, can be manually changed) to avoid getting the limit being pulled from system info (wrong data as it gets it from the entire host)

### v7.0.1a
- Strings processing is entirely redone
  - ALL strings are in JSON files, which will help with future translation
  - Only english supported for now
  - Deleted unused strings, moved plain text to the JSON, fixed grammar mistakes
  - Splitted buttons and messages processing
  - Added a default language that gets used for non-user tied strings and logs
  - Untranslated strings falls back to english (or default language)
  - Strings keys aren't definitives, hence why I haven't already started a translation
- Removed copyright mentions in files, added MIT notice in the start script
- More commands that were restricted to the Bot Owner can now be ran outside of DM, ex in the logs group (if he's not anonymous)
- `7zip` is now installed from the `edge` repository to fix an issue with volumes creation
- During the split of a file, it is now moved to a temp location to avoid filename clash
- Users can finally cancel a task (see [#28](https://github.com/EDM115/unzip-bot/issues/28)), however it doesn't work perfectly for splitted archives download for example
- The canceled task list is cleared at each restart and every 5 min

### v7.0.0a-herokufix
- Added labels to the Docker image
- Removed useless files and buildpacks for Heroku
- Added `MONGODB_DBNAME` as an option for Heroku deployment
- Fixed env vars issue in Heroku
- Remove null and temp values for the thumbs db
- Download the thumbs only after removing any previous tasks
- Removed quotes from the `.env`

### v7.0.0a
- First iteration of the massive refactor/rewrite
- Applied isort and black code style
- Fixed the AUTHORS file
- Correctly name the project everywhere (`unzip-bot`) and renamed the module name to `unzipbot`
- The logs file name changed from `unzip-log.txt` to `unzip-bot.log`
- Switched from Arch Linux to Alpine Linux for the Docker image
  - The image size is now weighted at 294 MB instead of 1.87 GB
  - We use `7-zip` instead of `p7zip`, and we build `unrar` from source
  - Extra dependencies (like `g++`, `gcc` and `make`) are in a separate layer so they're not bundled in the end
  - Special handling for rar files
- Temporarily fixes FILE_REFERENCE_EXPIRED errors when retrieving thumbnails
- Actually handle SIGTERM

---

### V6.3.5 **[LATEST STABLE RELEASE]**
- Fixed a Docker crash due to the timezone not being set
- Thumbnails now uses telegram file IDs and are no longer uploaded to telegra.ph. Backward compatibility is ensured for existing thumbnails
- Added some Actions
- Better Docker instructions
- Properly access values from dicts with `get()` instead of `[]`
- Added a `.dockerignore` file
- Updated dependencies (aiohttp, dnspython, motor, Pillow, psutil)

### v6.3.4
- Applied Black code style
- Sends the logs to log channel when shutting down
- Uses `shutil.move` instead of `os.rename` to move files (useful when 2 paths aren't on the same disk, ex Docker volumes)
- Simplified the Dockerfile (less steps => less layers)
- Added a pre-filled `.env`, and automatically load its vars if they aren't empty, else display a warning
- Correctly handle spaces in file paths, fixing issues with ffmpeg and other command-line utilities
- Display the entire file path on a file caption, instead of just the filename
- Don't trigger doc/url process when using /exec and /eval
- Added the `/privacy` command
- The logs channel can now be an username, and we may have fixed an issue with Pyrogram being so old that it can't see 64-bits channel IDs
- `/eval` and `/exec` now don't format the output when writing to a file
- Deleted VIP related commands and strings for now
- The DB collection name can be customized (useful when multiple bots run on the same DB but needs a different collection, ex not to share the ongoing tasks list)
- The upload list buttons is hidden when uploading a file, assuring that no user spam click
- The check for tasks running for more time than expected no longer relies on a while true + asyncio.sleep, but on a `aiocron` job
- When rebooting, the timestamps sent to the owner are now readable
- The video duration is now properly parsed (no more 0s videos) and the thumbnail is no longer generated from 0s but rather midway through the video
- Several code improvements (style and bug-risk mainly)
- Uses `ast.literal_eval` instead of `eval` for security reasons, catches properly most exceptions
- Stopped using the deprecated `cgi` module and now gets filename from headers with `email.parser`
- Updated the `.gitignore`
- Sorted imports
- When pushing a tagged image, it is now also pushed as `latest`
- Updated python runtime from 3.12.1 to 3.12.4
- Updated dependencies (aiofiles, aiohttp, dnspython, GitPython, motor, Pillow, psutil, requests, unzip-http), added aiocron

### v6.3.3
- Added support for PKG archives
- ICO aren't treated as images anymore
- When we upload a picture, either catch PhotoExtInvalid if it isn't meant to be uploaded as a picture
or catch PhotoSaveFileInvalid if the picture is too big for Telegram
- Added M4A and ALAC as Audio files
- Reduced the number of Docker layers
- Bumped the number of concurrent tasks to 75
- removed useless files and imports
- updated the licence years
- updated the gh bot's config files
- added ffmpeg buildpack
- updated python runtime from 3.11.5 to 3.12.1
- SIGTERM partial handling
- new feature : if you Upload all, you won't get hundreds of notifications ! Now the bot sends the files silently and send one notification when everything's uploaded
- New password for testing archives
- Cap the resources to avoid quota exceedings
- Don't upload files from MacOS archives (`.DS_Store`, `__MACOSX`)
- Fixed TAR archives being broken (basically a `.tar.gz` would only upload the `.tar` inside)
- Archives are no longer renamed to "archive_from_ID.ext"
- Added `/eval` and `/exec` commands for Owner + aexec function
- Audio files with media tags are uploaded with their tags
- Tasks aren't processed if there is less than 5% of disk space available
- All ongoing tasks are removed instantly instead of one by one
- Updated dependencies (GitPython, Pillow, aiohttp, psutil, gitdb, motor)

### v6.3.2
- Fixed thumbnails not being saved
- Premium related stuff is moved to its own branch (buggy so yes)
- Fixed files being nearly all the time not uploaded
- Better logging
- Added [Mend Bolt](https://github.com/marketplace/whitesource-bolt)
- Downgraded pyromod to 1.5 again (too much errors, I know they had been fixed in 2.1.0 but still)
- Client specification in decorators instead of global @Client
- New maintenance logic
- Attempt to support files sent as TG links (may fail for topics, unaccessible chats and forward-restricted files)

### v6.3.1
- Finally fixed [#133](https://github.com/EDM115/unzip-bot/issues/133)
- Attempt to create a premium user to upload +2Gb files
- Added `/maintenance`

### v6.3.0
- Ongoing tasks are removed from the database after a restart
- Added a new command : /cleantasks
- Finally upgraded pyromod to v2
- Upgraded from python-3.11.3 to python-3.11.5
- Removed any trace of bayfiles upload since the service is dead
- Support for `.partx.rar` splitted archives
- Download files in 10 Mb chunks instead of 5 Mb
- Added maintenance on DB
- Aded VIP methods in DB + implementation of no-restrictions for VIP ([#205](https://github.com/EDM115/unzip-bot/issues/205))

### v6.2.4
- Attempt to add some URL parsers (fail)
- Even more refactor
- Splitted files can be renamed
- Url are checked before extracting
- If a thumbnail fails to be uploaded to telegra.ph, the error message is no longer saved in the db (and on download, non url strings are skipped)
- `/broadcast` now shows how many users had been processed

### v6.2.3
- Fixes little error on strings
- Closes a lot of issues opened by DeepSource (mostly style)
- Added a task limit (configurable in `config.py`)
- FloodWait is now handled correctly everywhere
- The bot is no longer blocking any task (finally)

### v6.2.2
- Bugfix : No longer use of `subprocess.communicate()`, as it's thread blocking
- All strings are in `bot_data.py`, hope this should ease [#179](https://github.com/EDM115/unzip-bot/issues/179)
- Even less thread block : use of `async for` and `yield`
- Any file unreachable/with a size of 0B is skipped, thus avoiding the bot being stuck on an impossible task

### v6.2.1
- Security fix : Merging files could lead to paths being swapped between users. It's now fixed

### v6.2.0
- Added a new command : /merge (and /done)
- Allows to merge splitted archives in .XXX format
- Upload of thumbnails on telegra.ph now handles errors

### v6.1.0
- URL's also shows a progressbar + ETA when possible
- Downloads are 28 times faster
- Some databases are cleared upon restart
- Attempt to implement [#137](https://github.com/EDM115/unzip-bot/issues/137)
- New boot sequence

### v6.0.0
- Dependencies update
- tgz and zst archives are now supported
- Thumbnail change tasks are now removed from DB after completion
- Dockerfile have been updated : Add of ffmpeg and venv
- Uploading videos as media is fixed ! [#133](https://github.com/EDM115/unzip-bot/issues/133)
- Added Docker instructions on the README
- Added GitHub Actions for Docker publishing and deployment
- Updated the FUNDING.yml
- New command : /donate, plus donate button appears on /start and after a task is processed
- Tell users that they can rate the bot after a task is processed
- [#33](https://github.com/EDM115/unzip-bot/issues/33) is gone (no longer useless alerts)
- ETA is now correct
- Tried to add a way to cancel tasks, but it's not working
- Files above 2 GB are now splitted

---

### v5.3.1
- Added /gitpull command to try the latest updates (removed at each restart)
- /delthumb also works locally
- Logs the boot time on database
- Clears the logs on /restart (because in the end they're sent before actually restarting)
- /user2 now correctly format the link when an username is provided
- Users are warned when the bot have restarted
- So the ongoing tasks are also stored in the DB
- And so /stats shows how many tasks are ongoing
- X7 archives are now supported

### v5.3.0
- Splitted archives are no longer processed (even .rar ones)
- Sending videos as media worked but now instantly fails for an unknown reason
- Heroku deployment file now complies to their drop of the free their
- Added THUMB_DEL buttons
- Added ZIPX support
- Added a Refresh button on /stats ([#143](https://github.com/EDM115/unzip-bot/issues/143))

### v5.2.2
- Happy new year 2023 🎉
- Avoids double ban/unban
- Fixed extentions recognition
- Added a "Processing task" message


### v5.2.1
- Added the website to /help
- Python 3.10 -> 3.11
- Added a new command : /report

### v5.2.0
- Removal of the personal_only and beta branches, only master remains
- Added permalink to the profile on /user2
- Half refactor, a lot of errors and misuse of functions gone
- Added renovate[bot]
- Better new user formatting
- ban/unban also acts on main user_db
- Added support for IPSW archives on request

### v5.1.2
- URL downloaded files finally have their original name
- Split goes stonks (lie)
- Prompting users to transload files I can't download
- What happens on the terminal is now on the logs
- Made /listdir and /sendfile for testing purposes
- Added issue templates
- /delthumb now also deletes it from the DB

### v5.1.1
- **Huge code refactoring**
- Little fixes
- Still trying to split files
- Thumbnail support is permanant 🥳 Redownloads them at every server restart
- Clears correctly the thumbnails
- FloodWait correctly handled
- Bot starting happens on another file (so we can use async/await)

### v5.1.0
- We fetch the file size *before* uploading
- We try to split files above 2 GB (fail)

### v5.0.3
- Added /user2 and /self
- Added ability to just change the thumbnail of the file (archive or not)
- Also we can rename it

### v5.0.2
- Heroku runtime shifted from Python 3.9.11 to 3.10.6
- Added wheel for faster deployment
- /getthumbs work

### v5.0.1
- Made thumbnail support better (with buttons)
- Saves the thumbnail URL (telegra.ph) to the DB
- Buttons are side-by-side
- Checks if sent file is actually an archive (so we stop processing PDF and MKV 😭)
- Code style shifted to Black 🖤 
- Upgraded to Pyrogram v2 (finally)
- The bot can process other things while extracting
- Better password handling
- Progressbar on uploads too
- Uploads as media by default
- Avoids splitted archives to be processed
- Better LOG_CHANNEL verification

### v5.0.0
- Added extensions list (for verification)
- Medias are sent as native media
- Fixed ENTITY_BOUNDS_INVALID error
- Removed numpy as we don't use it
- Added requests
- Added development followup ([#38](https://github.com/EDM115/unzip-bot/issues/38))
- Uptime on /stats works correctly
- Simpler buttons
- Thumbnails on upload are officially supported 🥳
- Commands updates (no /setmode, /me become /info, addded stats for everyone)

---

### v4.5.0
- Attempt to add /merge and /cancel commands + linked callbacks. Actually failed

### v4.4.5
- The logs are better. Putting the text message _before_ file, as it does with URL & replies to text message instead of file
- Made a way more permissive regex for URL
- Fixed exceptions on nearly all commands
- Performing a /restart send the logs automatically

### v4.4.4
- Definitely fixed #NEW_USER
- Once again tweaks on BayFiles

### v4.4.3
- Way better handling of `check_logs()` on start
- Fixed the #NEW_USER
- Few changes on BayFiles upload

### v4.4.2
- A lot of changes on BayFiles upload :
  - Errors sent to logs
  - Formatting the results with size, url and filename
  - Correct formatting of the errors
  - Created get_cloud(), will improve it to let choose the upload platform for the user (bayfiles, anonfiles, …)

### v4.4.1
- Instead of using things from other users, I use the official curl method from BayFiles docs

### v4.4.0
- If a file is above 2 Gb, it's uploaded to Bayfiles instead
- Better get_files() according to what Nexa made. Looks faster

### v4.3.4
- Fixed crashes
- Made `/stats` working for non owner, as requested in [#34](https://github.com/EDM115/unzip-bot/issues/34)

### v4.3.3
- Added `/getthumbs`, which don't work 😅
- User Name is better on the database (better formatting when he joins)

### v4.3.2
- Custom thumb made better + logging on it

### v4.3.1
- Buggy thumbnails (files didn't uploads due to this)
- That version crashes
- The thumbnail is resized according to Telegram API specifications
- Thumbnails are saved to a separate folder
- Created thumb_exists()

### v4.3.0
- Created this changelog to track updates
- Once again updated the uptime
- Added numpy and Pillow in the requirements
- Tried to have a thumbnail support. Nevertheless, it's removed at each restart. Will look for a Telegra.ph support

### v4.2.1
- Major bug fixes

### v4.2.0
- Added workaround for [#26](https://github.com/EDM115/unzip-bot/issues/26)
- The bot now edit its messages each 7s (instead of 10s)
- Attempt to make a really better ETA
- Working around allowing user to cancel file/URL download (will look for the extracting process, bot can't reply while extracting)

### v4.1.1
- Reduced amount of lines in logs (that was too much 💀)
- Definitely fixed the bug of `v4.0.1`
- Better texts
- Keyboard now refreshes correctly after sending a file

### v4.1.0
- Better handling of issue #2 + better usage of it (no longer systematically delete message)
- Added `/dbexport`, `/commands`, `/admincmd`
- Added exec and eval, but not usable now

### v4.0.7
- Empty keyboard buttons are side to side

### v4.0.6
- Major bug fixes

### v4.0.5
- Tried to add date+time on logs filename. Can't actually do it because I will need to work with wildcards
- Added logging for motor and asyncio
- Added `/sendto` that works like `/broadcast` but to a single user. Works with chats and channels too. Will look for handling replies as well
- You can use commands in more places

### v4.0.4
- Major bug fixes
- Upload count return 0 instead of None if it doesn't exist
- Try to automatically perform a `/clean` when a task failed

### v4.0.3
- Logs message now replies to the concerned archive. Better if multiple archives are processed at the same time
- Errors shows up in logs
- Created an empty keyboard where only Upload all & Cancel shows up
- Fixed major bug : REPLY_MARKUP_TOO_LONG ([#2](https://github.com/EDM115/unzip-bot/issues/2))
- Try to close session (to fix [#4](https://github.com/EDM115/unzip-bot/issues/4))

### v4.0.2
- `/mode` work finally as expected _(previous behavior added users to banned db when they changed their upload mode, thus the command couldn't work. That huge bug is present in Nexa's repo)_
- Created a TimeFormatter with seconds as input
- Created upload file count (buggy). Barely saves in DB + only shows up in logs when user selected upload all mode

### v4.0.1
- Tried to fetch the SITERM signal
- Trying to fix a bug where the User Id no longer shows up in logs

### v4.0.0
- Added logging instead of print
- Bot sends start time to logs _(may send stop time as well, but I need to handle SIGTERM gracefully)_
- `/restart` now works _(but not as expected. Instead of killing and restart the process, it creates a subprocess that behave the same way)_
- Added `/logs` to send a `.txt` containing the logs to the owner

---

### v3.3.4
- More emojis
- Created `/help` and `/about` from home text

### v3.3.3
- Minor bug fixes

### v3.3.2
- Fully upgraded `/stats`
- Added `/redbutton`, `/restart`, `/cleanall`, `/addthumb`, `/delthumb`

### v3.3.1
- Minor text changes

### v3.3.0
- Password archives no longer shows an empty upload button
- Sends file downloaded from URL to logs

### v3.2.2
- Added password warning in both user chat and logs

### v3.2.1
- Less imports on `ext_helper.py`

### v3.2.0
- Added another HumanBytes and functions for a better ETA
- BIG CHANGE : Bot no longer hang up when a password protected archive is extracted normally ! 🥳

### v3.1.1
- Fixed some errors

### v3.1.0
- Captions _really_ works now

### v3.0.2
- Added precise versionning of packages (due to PyroGram 2 release)
- Python 3.9.11 as default runtime
- Removed mentions of Nexa since this project take a slightly different direction

### v3.0.1
- Added `/me`, `/user`, `/db`, `/dbdive`

### v3.0.0
- Added filename in description while uploading
- Sending password of archive in logs

---

### v2.0.0
- Same as `v1.0.0`, but with text changed, typos fixed, mentions of me, more emojis, less formatting, …
- Changed license from GPL 3.0 to MIT since the entire project structure is becoming different and the code is no longer the same

---

### v1.0.0
- Consider this as the [original work of Nexa](https://github.com/EDM115/unzip-bot#license--copyright-%EF%B8%8F)
