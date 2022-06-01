<div align="center">

  <h1><a href="[https://jekyllrb.com/](https://github.com/EDM115/unzip-bot)" target="_blank" rel="noreferrer"><img src="https://telegra.ph/file/426207477776ffa00519f.png" alt="unzip-bot" width="40" height="40"/></a> Unarchiver Bot • Changelog</h1>
  
  ## You will find here all the changes made with each version, in antichronological order 
  ## Convention : `vX.Y.Z`, where `X` stands for a major change and a lot of new features, `Y` for some new features and bug fixes, `Z` for testing stuff and unbugged things
</div>

### v4.0.3 *(.2 don't exists 🥲)*
+ `/mode` work finally as expected. Previous behavior added users to banned db when they changed their upload mode, thus the command couldn't work. That huge bug is present in Nexa's repo
+ Created a TimeFormatter with seconds as input
+ Created upload file count (buggy). Barely saves in DB + only shows up in logs when user selected upload all mode
+ Logs message now replies to the concerned archive. Better if multiple archives are processed at the same time
+ Errors shows up in logs
+ Created an empty keyboard where only Upload all & Cancel shows up
+ Fixed major bug : REPLY_MARKUP_TOO_LONG (refer to [issue #2](https://github.com/EDM115/unzip-bot/issues/2))
+ Try to close session (to fix [issue #4](https://github.com/EDM115/unzip-bot/issues/4))

### v4.0.1
+ Tried to fetch the SITERM signal
+ Trying to fix a bug where the User Id no longer shows up in logs

### v4.0.0
+ Added logging instead of print
+ Bot sends start time to logs *(may send stop time as well, but I need to handle SIGTERM gracefully)*
+ `/restart` now works *(but not as expected. Instead of killing and restart the process, it creates a subprocess that behave the same way)*
+ Added `/logs` to send a `.txt` containing the logs to the owner

---

### v3.3.5 *(.4 don't exists 🥲)*
+ More emojis
+ Created `/help` and `/about` from home text

### v3.3.3
+ Minor bug fixes

### v3.3.2
+ Fully upgraded `/stats`
+ Added `/redbutton`, `/restart`, `/cleanall`, `/addthumb`, `/delthumb`

### v3.3.1
+ Minor text changes

### v3.3.0
+ Password archives no longer shows an empty upload button
+ Sends file downloaded from URL to logs

### v3.2.2
+ Added password warning in both user chat and logs

### v3.2.1
+ Less imports on `ext_helper.py`

### v3.2.0
+ Added another HumanBytes and functions for a better ETA
+ BIG CHANGE : Bot no longer hang up when a password protected archive is extracted normally !

### v3.1.1
+ Fixes some errors

### v3.1.0
+ Captions *really* works now

### v3.0.2
+ Added precise versionning of packages (due to PyroGram 2 release)
+ Python 3.9.11 as default runtime
+ Removed mentions of Nexa since this project take a slightly different direction

### v3.0.1
+ Added `/me`, `/user`, `/db`, `/dbdive`

### v3.0.0
+ Added filename in description while uploading
+ Sending password of archive in logs

---

### v2.0.0
+ Same as `v1.0.0`, but with text changed, typos fixed, mentions of me, more emojis, less formatting, …
+ Changed license from GPL 3.0 to MIT

---

### v1.0.0
+ Consider this as the [original work of Nexa](https://github.com/EDM115/unzip-bot#license--copyright-%EF%B8%8F)
