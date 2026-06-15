# Part 1
This solves the following points :
- Refactor everything, separate functions (see https://github.com/EDM115/unzip-bot/issues/267)
- Database rework (https://github.com/EDM115/unzip-bot/issues/356)
- Optimize the recurrent tasks (see https://github.com/EDM115/unzip-bot/issues/285, done but ensure it does work well)

## Steps
- [x] 1) Move all usage to the new built-in config (old one used a config.py file at project's root, now deleted)
- [x] 2) Finish the "orm-lite", make sure we have all operations we could need on both mongodb & sqlite. Ensure the "base" allows us to create an object that calls either mongodb or sqlite depending on what we need. Refer to https://github.com/EDM115/unzip-bot/issues/356
- [x] 3) Make sure we can have a proper way to "init" the sqlite db (create tables and relations). The sqlite db is only here to act as a local mirror of the mongodb one, and hold data that don't need to be stored in the cloud (ex the Task table). when the bot starts, it "dumps" the data from mongodb atlas into sqlite, all operations (read/write) happen on sqlite and write operations (create/update/delete) are mirrored to atlas
- [x] 4) Analyze current usage in helpers/database.py and map that current usage to db/functions.py with the "orm-lite". keep in mind that we should support both existing data and users who deploy the bot for the first time and have none
- [x] 5) Analyze current usage of cli tools and write appropriate functions in the cli/tools dir (ex for 7z.py, functions like extract, extract_password, test, ...)
- [x] 6) Analyze and move the current behavior (in modules dir) to the pre-made new structure (plugins & utils). Note that plugins have a special meaning in the Pyrogram client world, make sure to understand that
- [x] 7) Check that init and main files will still behave correctly (ex plugins dict init)
- [x] 8) Review against docs that the current async bot start and stop handling is correct
- [x] 9) Review cleanup (when a task finishes/is cancelled), proper cancellation, ...

---

# Part 2
This second part will help with the following :
- Simplify the commands list, make a unified settings page (see https://github.com/EDM115/unzip-bot/issues/173)
- Allow to cancel downloads (the button works-ish, but split archives processing doesn't get cancelled properly) (see https://github.com/EDM115/unzip-bot/issues/28 & https://github.com/EDM115/unzip-bot/issues/245)
- Global cleanup phase (type everything, run type-checking with `ty`)
- Enhancements

## Steps
- [ ] 1) Allow users to edit their settings using a menu with buttons
- [ ] 2) BOT_OWNER should have a different one
- [ ] 3) Actually, we should allow multiple bot owners (separated by commas in the env var). See https://github.com/EDM115/unzip-bot/issues/288, also implement whitelist feature in the admin options
- [ ] 4) Continue the implementation of interfaces if it is needed somewhere else (see https://github.com/EDM115/unzip-bot/issues/401)
- [ ] 5) Expose a port and run an API to get some stats, useful for both monitoring the bot's health and get real-time insights (see https://github.com/EDM115/unzip-bot/issues/452). Overall expose the bot health, uptime, stats (storage, ram, cpu, ... review current way to pull those infos), and overall stats (processed files, links, amount of data). Since we don't have this data (yet), I will insert an approximation in atlas and we can start from it
- [ ] 6) Allow to browse the archives much better (not to the point where I implement a search, but still something better that a dumb list of 96 items) (see https://github.com/EDM115/unzip-bot/issues/169, https://github.com/EDM115/unzip-bot/issues/174, https://github.com/EDM115/unzip-bot/issues/309). users should be able in their settings to choose between "folder" or "list" modes when presented with the files list. keep in mind hierarchy, going back and forth folders, an ability to upload a whole folder and its contents (?), upload all, cancel and pagination
- [ ] 7) Check the code for performance issues, type errors, duplicated content, ... Also ensure everything is strictly type-checked
- [ ] 8) Extract splitted archives from multiple URL (see https://github.com/EDM115/unzip-bot/issues/306)

# Part 3
Overall goals :
- VIP system
- Completely optional, allow devs to deploy their own version where the system doesn't exist and all vip-gated features are available to everyone
- Documentation

## Steps
- [ ] 1) The VIP plan is described here : https://github.com/EDM115/unzip-bot/issues/205. It would require a better way to add/edit/remove vip users than the half-baked commands we have. for the multiple tasks part, it would also require to rework how tasks are currently handled (userid/task_num/folder ?)
- [ ] 2) Add a way to run multiple clients. This should be entirely opt-out, where we have our in-house "load-balancer". if there's only one client (current behavior), it treats user requests (messages, commands), downloads and uploads. the idea is to keep a "front-facing" bot (main one), that *could* then fire a request to the load-balancer for tasks that generate `FloodWait`'s. Bypassed when there's only one bot, the dev can describe at image build time (env vars ? how do we pass multiple tokens (or api id/hash/tokens triplets) ?), so download requests are handled by one of the download bots. they get passed the link(s) or id of the telegam file(s) and retrive them on the server. for upload requests, the files are uploaded from the server to a group chat that will store the filer temporarily. in description they will have the filepath, userid and potentially taskid. the main bot will either forward the message with only the filepath as caption (as it is now), or use send_file with the existing id. if a bot faces timeouts during upload, the rest of the files is picked up by another available bot (if any, otherwise just wait the indicated time). it's the **main bot** that deletes the files on the server, only when it properly sent/forwarded the message to the user to ensure no issues
- [ ] 3) Enhance interface so users have a better glimpse at what happens (see https://github.com/EDM115/unzip-bot/issues/176 & https://github.com/EDM115/unzip-bot/issues/204)
- [ ] 4) fix : A telegram link that points to an archive should be processed
- [ ] 5) Save a list of passwords to try (see https://github.com/EDM115/unzip-bot/issues/144, as well as a list of thumbnails. 3 for free users, 10 for premium ones
- [ ] 6) Setting to auto-upload, or upload all after a period of inactivity (see https://github.com/EDM115/unzip-bot/issues/313). also see https://github.com/EDM115/unzip-bot/issues/322
- [ ] 7) Review & implement feature requests & bugs :
  - [ ] bug : https://github.com/EDM115/unzip-bot/issues/329 (seems to have self-corrected)
  - [ ] bug : https://github.com/EDM115/unzip-bot/issues/374. this is likely related to accumulated floodwaits, which the refactor will fix
  - [ ] bug : with filenames (see https://github.com/EDM115/unzip-bot/issues/342 & https://github.com/EDM115/unzip-bot/issues/375)
  - [ ] request : https://github.com/EDM115/unzip-bot/issues/336
  - [ ] request : https://github.com/EDM115/unzip-bot/issues/323
- [ ] 8) Add a proper documentation of the code. like seriously, i hate how bad it is for newcomers to understand how things work here
- [ ] 9) Update the README to reflect the changes (see https://github.com/EDM115/unzip-bot/issues/240)
