# Copyright (c) 2022 - 2024 EDM115
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup


class Messages:
    # here

    HELP = "Help 📜"

    ABOUT = "About 👀"

    STATS_BTN = "Stats 📊"

    DONATE = "Donate 💸"

    REFRESH = "Refresh ♻️"

    BACK = "Back 🏡"

    CLEAN = "Clean my files 🚮"

    AS_DOC = "As document 📁"

    AS_MEDIA = "As media 📺"

    MERGE_BTN = "Merge 🛠️"

    CHECK = "Check 👀"

    REPLACE = "Replace ⏭"

    SAVE = "Save 💾"

    DELETE = "Delete 🚮"

    RATE = "Rate me ⭐"

    # start.py

    PRIVATE_CHAT = "A private chat can't be used"

    NO_LOG_ID = "No log channel ID have been provided"

    ERROR_LOG_CHECK = "An error happened while checking the log channel 💀 Make sure you haven't provided a wrong log channel ID 🧐"

    DL_THUMBS = "Downloading {} thumbs"

    DOWNLOADED_THUMBS = "Downloaded {} of {} thumbs"

    BOT_RESTARTED = """
Bot restarted !

**Old boot time** : `{}`
**New boot time** : `{}`
    """

    RESEND_TASK = """
⚠️ **Warning** : the bot restarted while you were using it
Your task was stopped, kindly send it again
    """

    TASK_EXPIRED = """
Your task was running for more than {} minutes, it has been stopped

Don't go AFK next time 😉
    """

    # database.py

    BANNED = """
**Sorry you're banned 💀**

Report this at @EDM115_chat if you think this is a mistake, I may unban you
    """

    NEW_USER_BAD = """
**#NEW_USER** 🎙

**User profile :** `{}`
`[AttributeError]`
    """

    NEW_USER = """
**#NEW_USER** 🎙

**User profile :** `{}` {}
**User ID :** `{}`
**Profile URL :** [tg://user?id={}](tg://user?id={})
    """

    # unzip_help.py

    UNKNOWN_SIZE = """
**Size :** Unknown

This may take a while, go grab a coffee ☕️
    """

    PROGRESS_MSG = """
{}
{}

**Powered by @EDM115bots**
    """

    PROCESSING = "**Processing…**"

    SPEED = "**Speed :**"

    ETA = "**ETA :**"

    # __main__.py

    START_TXT = "ℹ️ The bot have successfully started at `{}` 💪"

    STOP_TXT = "ℹ️ The bot goes sleeping at `{}` 😴"

    STARTING_BOT = "Starting bot…"

    CHECK_LOG = "Checking log channel…"

    LOG_CHECKED = "Log channel checked"

    BOT_RUNNING = "Bot is running now ! Join @EDM115bots"

    WRONG_LOG = """
Error : the provided **LOGS_CHANNEL** (`{}`) is incorrect
Bot crashed 😪
    """

    # callbacks.py

    MAX_TASKS = """
Sorry, the bot is currently full 🥺

{} tasks are already running, please wait a few minutes
    """

    CHOOSE_EXT_MODE = """
Select the extraction mode for that {} 👀

{} : **Normal mode**
🔐 : **Password protected**
🖼️ : **Change the thumbnail**
✏ : **Change the thumbnail and rename the file**
❌ : **Cancel your task**
    """

    CHOOSE_EXT_MODE_MERGE = """
Select the extraction mode for that merged file 👀

🗂️ : **Normal mode**
🔐 : **Password protected**
❌ : **Cancel your task**
    """

    EXT_CAPTION = """
`{}`

Successfully extracted by @unzip_edm115bot 🥰
    """

    REPORT_TEXT = """
📢 --Report sent--

**User :** `{}`
**Message :** `{}`

#Report #Action_Required
    """

    LOG_CAPTION = """
**The file : ** `{}`

have been saved from the URL

`{}`
    """

    EXT_FAILED_TXT = """
**Extraction failed 😕**

**What to do ?**

   • Please make sure archive isn't corrupted
   • Please make sure that you selected the right mode !
   • Also check if you sent the right password (it's case sensitive)
   • Maybe your archive format isn't supported yet 😔


**⚠ IN ALL CASES ⚠**, please send **/clean**, else you can't send any other task 🙂🔫

Please report this at @EDM115_chat if you think this is a serious error
    """

    HOW_MANY_UPLOADED = "`{}` file(s) have been extracted from that archive"

    PLS_REPLY = "You need to reply ↩️ to a picture with this command for saving it as custom thumbnail 🤓"

    UPLOADING_THIS_FILE = "Uploading this file… Please wait"

    NO_MERGE_TASK = """
There's no merge task ongoing
Use **/merge** to start one
    """

    LOG_TXT = """
**Extract log 📝**

**User ID :** `{}`
**File name :** `{}`
**File size :** `{}`
    """

    PASS_TXT = """
**Password of the above archive is 🔑**

`{}`
    """

    DL_URL = """
**Downloading… Please wait**

**URL :** `{}`

    """

    REFRESH_STATS = "Refreshing stats… ♻️"

    ACTUAL_THUMB = "Your actual thumbnail"

    START_TEXT = """
Hi **{}** 👋, I'm **Unarchiver bot** 🥰

I can extract any archive, with password or not, splitted, …
Send **/commands** to learn more

**Made with ❤️ by @EDM115bots**
**/donate** if you can 🥺
    """

    HELP_TXT = """
**• How to extract 🤔**

    **1)** Send the file or link that you want to extract
    **2)** Click on extract button (If you sent a link use `🔗` button. If it's a file just use `🗂️` button)


**• How to change upload mode 🤔**
    Send **/mode**


**Note :**
    **1.** If your archive is password protected select `🔐` button
    **2.** Please don't send corrupted files ! If you sent one by mistake just send **/clean**
    **3.** If your archive have +95 files in it then bot can't show all of extracted files to select from (yet). So in that case if you can't see your file in the buttons just click on `Upload all 📤` button. It will send all extracted files to you !


**• Got an error ?**
    Visit edm115.dev/unzip#help


**• I wanna have help 🥺**

    PM me at **@EDM115** or join the chat **@EDM115_chat**
    """

    ABOUT_TXT = """
**About Unarchiver bot [v6.3.5]**

• **Language :** [Python 3.12.4](https://www.python.org/)
• **Framework :** [Pyrogram 2.0.106](https://pyrogram.org/)
• **Source code :** [EDM115/unzip-bot](https://github.com/EDM115/unzip-bot)
• **Developer :** [EDM115](https://github.com/EDM115)

**[Rate me ⭐](https://t.me/BotsArchive/2705)**
Made with ❤️ by **@EDM115bots**
    """

    DONATE_TEXT = """
I'm going to be honest : **this bot costs me money**…
Nothing's free on this world, however I try to keep this bot for free for as many people as possible
I don't like to put restrictions, nor getting your PM's flooded with ads…

So if you can, donate :)
It helps out a ton, covers the costs (hosting, updating, … 👨‍💻)

--How ?--
• **[Paypal](https://www.paypal.me/8EDM115)**
• **[GitHub Sponsors](https://github.com/sponsors/EDM115)**
• **[Directly in Telegram](https://t.me/EDM115bots/698)**
• **[BuyMeACoffee](https://www.buymeacoffee.com/edm115)**

Thanks for your contribution 😊

--Side note :--
Donation doesn't count as a VIP subscription. Check **/vip** for more info
    """

    VIP_INFO = """
--**NOT AVAILABLE YET !**--

Wanna help the developer of this __amazing__ bot ?
Here's how : Become a VIP user and benefit from extra perks !

**VIP perks :**
- No max tasks limit
- No AFK timeout
- Get a better support
- Upload files up to 4Gb
- Early access to new features
- Access a second bot exclusive to VIPs __(subject to conditions)__
- And more…

**What's the price ?**
- `1$/month`
- `10$/year`

**How to become a VIP ?**
1) Send **/pay** to the bot
2) Choose your subscription
3) Send a screenshot of your payment to **@EDM115**
4) Enjoy your VIP perks !

**What happens when my subscription ends ?**
If you choosed GitHub Sponsors, Telegram Donate or BuyMeACoffee, you will be automatically renewed until you cancel it
If you choosed PayPal, you will have to redo the 4 above steps
You will be notified few days before you subscription ends so you can check if you want to renew it or not

**I wanna cancel my subscription**
Just send **/stoppay** and follow the instructions according to the platform you selected
Your payment will be cancelled and you will keep your VIP perks until the end of your subscription
(i.e. if you paid for 1 month, from 05/01/2024 to 05/02/2024 and you cancel your subscription on 15/01/2024, your perks will stay until 05/02/2024)

**What is the referral system ?**
Referrals have benefits for both sides :)
- For the referrer : you get 1 month of VIP for free for each 3 new VIPs you bring
- For the referred : you get 1 month of VIP for free if you take the monthly subscription, and 3 months for free if you take the yearly subscription
How to input the referral code ? Just send **/pay** to the bot and follow the instructions
    """

    VIP_REQUIRED_MESSAGE = """
Use this command as a reply to a messsage, where you have the following (ONE PER LINE) :
The user ID (int)
When the subscription starts (in %Y-%m-%dT%H:%M:%SZ format)
When the subscription ends (same)
Which platform had been used [paypal, telegram, sponsor, bmac]
At which frequency the user is billed [monthly, yearly]
Is the user a early supporter (can be obtained only the first 3 months) [True, False]
Is the user also a donator [True, False]
When does the user ever started a subscription (date)
How many successful payments had been done (int)
Is there been any gap between payments [True, False]
If the user had been gifted a Premium plan [True, False]
The user referral code (str)
Is this a lifetime free subscription [True, False]
    """

    VIP_ADDED_USER = """
The following user had been added with the following infos :
User ID : `{}`
Start date : `{}`
End date : `{}`
Platform : `{}`
Frequency : `{}`
Early supporter : `{}`
Donator : `{}`
First subscription date : `{}`
Successful payments : `{}`
Gap between payments : `{}`
Gifted : `{}`
Referral code : `{}`
Lifetime : `{}`
    """

    CLEAN_TXT = """
**Are sure want to clean your task 🤔**

Note : This action cannot be undone
    """

    SELECT_UPLOAD_MODE_TXT = """
Select your upload mode 👇

**Current upload mode is :** `{}`
    """

    CHANGED_UPLOAD_MODE_TXT = "**Successfully changed the upload mode to** `{}` ✅"

    EXISTING_THUMB = """
A thumbnail already have been saved 😅 What you wanna do ?
• Check the actual thumbnail
• Replace it with the new one you just sent
• Cancel
    """

    SAVING_THUMB = "Are you sure you want to save this thumbnail 🤔"

    SAVED_THUMBNAIL = "**Successfully saved this thumbnail ✅**"

    DEL_CONFIRM_THUMB = """
Do you really want to delete your thumbnail ?
• Check the actual thumbnail
• Delete it
• Cancel
"""

    DEL_CONFIRM_THUMB_2 = "Do you really want to delete your thumbnail ?"

    DELETED_THUMB = "**Successfully deleted your thumbnail ✅**"

    ERROR_THUMB_RENAME = "Error on thumb rename"

    ERROR_THUMB_UPDATE = "Error while updating thumb URL on DB"

    ERROR_TELEGRAPH_UPLOAD = "Error on Telegra.ph upload"

    ERROR_THUMB_DEL = "Error on thumb deletion in DB : {}"

    AFTER_OK_DL_TXT = """
**Successfully downloaded ✅**

**Download time :** `{}`
**Status :** Testing the archive… Please wait
    """

    AFTER_OK_MERGE_DL_TXT = """
**Successfully downloaded all {} files ✅**

**Download time :** `{}`
**Status :** Merging the archive… Please wait
    """

    AFTER_OK_MERGE_TXT = """
**Successfully merged ✅**

**Merge time :** `{}`
**Status :** Processing the archive… Please wait
    """

    AFTER_OK_TEST_TXT = """
**Successfully tested ✅**

**Test time :** `{}`
**Status :** Extracting the archive… Please wait
    """

    EXT_OK_TXT = """
**Extraction successful ✅**

**Extraction time :** `{}`
**Status :** Processing the extracted files… Please wait
    """

    ERROR_TXT = """
**Error happened 😕**

`{}`

Please report this at @EDM115_chat if you think this is a serious error
    """

    CANCELLED_TXT = "**{} ✅**"

    DL_STOPPED = "The download of your file have successfully been cancelled ✅"

    PROCESSING_TASK = "**✅ Processing your task… Please wait**"

    ERROR_GET_MSG = "Error on getting messages from user : {}"

    PROCESS_MSGS = "**Processing {} messages… Please wait**"

    DL_FILES = """
**Downloading file {}/{}… Please wait**

    """

    PROCESS_MERGE = """
Processing an user query…

User ID : {}
Task : #Merge

File : {}
    """

    PLS_SEND_PASSWORD = "**Please send me the password 🔑**"  # skipcq: SCT-A000

    PASSWORD_PROTECTED = "That archive is password protected 😡 **/clean** and retry"

    SELECT_FILES = "Select files to upload 👇"

    UNABLE_GATHER_FILES = """
Unable to gather the files to upload 😥
Choose either to upload everything, or cancel the process
    """

    FATAL_ERROR = "Fatal error : uncorrect archive format"

    USER_QUERY = """
Processing an user query…

User ID : {}
    """

    INVALID_URL = "That's not a valid url 💀"

    NOT_AN_ARCHIVE = """
That's not an archive 💀
    """

    DEF_NOT_AN_ARCHIVE = """
This file is NOT an archive 😐
If you believe it's an error, send the file to **@EDM115**
    """

    PROCESSING2 = "`Processing… ⏳`"

    UNZIP_HTTP = "Can't use unzip_http on {} : {}"

    ERR_DL = "Error on download : {}"

    CANT_DL_URL = "**Sorry, I can't download that URL 😭**"

    GIVE_ARCHIVE = "Give me an archive to extract 😐"

    ITS_SPLITTED = """
This file is splitted
Use the **/merge** command
    """

    SPL_RZ = "Splitted RAR/ZIP files in .rxx or .zxx format can't be processed yet"

    TRY_DL = """
**Downloading… Please wait**

    """

    QUERY_PARSE_ERR = """
Fatal query parsing error 💀

Please contact @EDM115_chat with details and screenshots
    """

    GIVE_NEW_NAME = """
Current file name : `{}`

Please send the new file name (**--INCLUDE THE FILE EXTENTION !--**)
    """

    SPLITTING = "**Splitting {}… Please wait**"

    ERR_SPLIT = "An error occured while splitting a file above 2 Gb 😥"

    SEND_ALL_PARTS = "Sending all parts of {} to you… Please wait"

    UPLOADED = """
**Successfully uploaded ✅**

**Join @EDM115bots ❤️**
    """

    NO_FILE_LEFT = "There's no file left to upload"

    SENDING_FILE = "Sending that file to you… Please wait"

    SEND_ALL_FILES = "Sending all files to you… Please wait"

    REFRESHING = "Refreshing… ⏳"

    CANCELLED = "**Cancelled successfully ✅**"

    PROCESS_CANCELLED = "❌ Process cancelled"

    # commands.py

    PRIVACY = "PRIVACY ??"

    PROCESS_RUNNING = """
Already one process is running, don't spam 😐

Send **/clean** if you want to process a new file
    """

    SPLIT_NOPE = "Those type of splitted files can't be processed yet"

    UNVALID = "Send a valid archive/URL"

    NO_SPACE = "There's no space left on the server 😥"

    MERGE = """
You have splitted archives to process ?
Send me **all** the splitted files (.001, .002, .00×, …)

**AFTER** you sent them all, send **/done** and click on the `Merge 🛠️` button
    """

    DONE = """
If you have sent **ALL** the files, you can click on the `Merge 🛠️` button below

If you sent /done by mistake and haven't sent all the files yet, just ignore this message and re-send **/done** after ALL the files are sent
    """

    STATS = """
**💫 Current bot stats 💫**

**💾 Disk usage :**
 ↳ **Total disk space :** `{}`
 ↳ **Used :** `{} - {}%`
 ↳ **Free :** `{}`
 ↳ **Ongoing tasks :** `{}`

**🎛 Hardware usage :**
 ↳ **CPU usage :** `{}%`
 ↳ **RAM usage :** `{}%`
 ↳ **Uptime :** `{}`
    """

    STATS_OWNER = """
**💫 Current bot stats 💫**

**👥 Users :**
 ↳ **Users in database :** `{}`
 ↳ **Total banned users :** `{}`

**💾 Disk usage :**
 ↳ **Total disk space :** `{}`
 ↳ **Used :** `{} - {}%`
 ↳ **Free :** `{}`
 ↳ **Ongoing tasks :** `{}`

**🌐 Network usage :**
 ↳ **Uploaded :** `{}`
 ↳ **Downloaded :** `{}`

**🎛 Hardware usage :**
 ↳ **CPU usage :** `{}%`
 ↳ **RAM usage :** `{}%`
 ↳ **Uptime :** `{}`
    """

    BC_REPLY = "Reply to a message to broadcast it 📡"

    BC_START = """
Broadcasting has started, this may take a while 😪

Users : {}/{}
    """

    BC_DONE = """
**Broadcast completed ✅**

**Total users :** `{}`
**Successful responses :** `{}`
**Failed responses :** `{}`
    """

    SEND_REPLY = "Reply to a message to send it 📡"

    PROVIDE_UID = "Please provide an user ID"

    PROVIDE_UID2 = "Please provide an user ID/username"

    SENDING = "Sending it, please wait… 😪"

    SEND_SUCCESS = "Message successfully sent to `{}`"

    SEND_FAILED = """
It failed 😣 Retry

If it fails again, it means that {} haven't started the bot yet (or deleted the chat), or he's private/banned/whatever
    """

    REPORT_REPLY = "Reply to a message to report it to @EDM115"

    REPORT_DONE = """
Report sucessfully sent ! An answer will arrive soon

Note : if you need to reply to replies, always use that /report command (or join **@EDM115_chat**)
    """

    BAN_ID = "Give an user id to ban 😈"

    ALREADY_BANNED = """
{} have already been banned


    """

    ALREADY_REMOVED = "{} have already been removed from the user database"

    USER_BANNED = """
**Successfully banned that user ✅**

**User ID :** `{}`
    """

    UNBAN_ID = "Give an user id to unban 😇"

    ALREADY_ADDED = """
{} is already in the user database


    """

    ALREADY_UNBANNED = "{} have already been deleted from banned users database"

    UNBANNED = """
**Successfully unbanned that user ✅**

**User ID :** `{}`
    """

    INFO = "Send a text (shorter possible) from any user/chat. And you will have infos about it 👀"

    USER = "This is a WIP command that would allow you to get more stats about your utilisation of me 🤓"

    UNABLE_FETCH = "Unable to fetch"

    USER_INFO = """
**User ID :** `{}`
`{}` files uploaded
…

WIP
    """

    UID_UNAME_INVALID = "Error happened, The user ID/username is probably invalid"

    USER2_INFO = """
`{}`

**Direct link to profile :** tg://user?id={}
    """

    MAINTENANCE = """
Do you want the bot to go in maintenance mode 🤔
Current state : `{}`
    """

    MAINTENANCE_ASK = """
False : No maintenance
True : Maintenance
Send the appropriate string
    """

    MAINTENANCE_DONE = "Successfully changed maintenance mode to `{}`"

    MAINTENANCE_ON = """
Maintenance mode is currently **ON**
Tasks can't be processed. Come back later
    """

    MAINTENANCE_FAIL = "Provide one of the values"

    NO_THUMBS = "No thumbnails on the server yet"

    ERASE_ALL = "**Cleaning…**"

    CLEANED = "The whole server have been cleaned ✅"

    NOT_CLEANED = "An error happened during /cleanall"

    ERASE_TASKS = "Deleting {} tasks… Please wait"

    ERASE_TASKS_SUCCESS = "Successfully deleted {} tasks ✅"

    LOG_SENT = "Log file sent to {}"

    DELETED_FOLDER = "Deleted {} folder successfully"

    RESTARTED_AT = "**ℹ️ Bot restarted successfully at **`{}`"

    RESTARTING = "{} : Restarting…"

    PULLING = "Pulling updates… ⌛"

    PULLED = "✅ Pulled changes, restarting…"

    NO_PULL = "Nothing to pull 😅"

    COMMANDS_LIST = """
Here is the list of the commands you can use (only in private btw) :

**{send any file or URL}** : Prompt the extract dialog
**/start** : To know if I'm online
**/help** : Gives a simple help
**/about** : Know more about me
**/donate** : Know how you can contribute to this bot
**/clean** : Remove your files from my server. Also useful if a task failed
**/mode** : Change your upload mode (either `doc` or `media`)
**/stats** : Know all the current stats about me
**/merge** : Merge splitted archives together
**/done** : After you sent all the splitted archives, use this to merge them
**/info** : Get full info about a [Message](https://docs.pyrogram.org/api/types/Message) (info returned by Pyrogram)
**/addthumb** : Upload with a custom thumbnail
**/delthumb** : Removes your thumbnail
**/report** : Used by replying to a message, sends it to the bot owner (useful for bug report, or any question)
**/vip** : __Not available yet__ Know more about the VIP subscription
**/commands** : This message
    """

    ADMINCMD = """
Here's all the commands that only the owner (you) can use :

**/gitpull** : Pulls the latest changes from GitHub
**/broadcast** : Send something to all the users
**/sendto {user_id}** : Same as broadcast but for a single user. Doesn't handle replies for now…
**/ban {user_id}** : Ban an user. He can no longer use your bot, except if…
**/unban {user_id}** : …you unban him. All his stats and settings stays saved after a ban
**/user {user_id}** : Know more about the use of your bot by a single user
**/user2 {user_id}** : Get full info about an [User](https://docs.pyrogram.org/api/types/User) (info returned by Pyrogram)
**/self** : Get full info about me (info returned by Pyrogram)
**/getthumbs** : Get all the thumbnails on the server
**/redbutton** : __Does nothing yet__
**/maintenance** : Put the bot in or out of maintenance mode. No tasks can be processed while on
**/cleanall** : Same as `/clean`, but for the whole server
**/cleantasks** : Same as `/cleanall`, plus removes them from the database
**/logs** : Send you the logs (all of them). Useful for bug tracking. Send them to **@EDM115** if you don't understand them/need help
**/restart** : Does a basic restart, less intrusive as the `/redbutton` one
**/dbexport** : ~~Exports the whole database as CSV~~ __Does nothing yet__
**/eval {code}** : Evaluate a piece of code. Useful for debugging
**/exec {code}** : Execute a piece of code. Useful for debugging
**/admincmd** : This message
**/commands** : For all the other commands
    """

    # custom_thumbnail.py

    ALBUM = "{} tried to save a thumbnail from an album"

    ALBUM_NOPE = "You can't use an album. Reply to a single picture sent as photo (not as document)"

    DL_THUMB = "Downloading thumbnail of {}…"

    THUMB_SAVED = "Thumbnail saved"

    THUMB_CAPTION = """
#thumbnail

Saved thumbnail of [user {}](tg://user?id={})
    """

    THUMB_FAILED = "Failed to generate thumb"

    THUMB_ERROR = "Error happened 😕 Try again later"

    NO_THUMB = "You already have no thumbnail 😅"

    # ext_helper.py

    UP_ALL = "Upload all 📤"

    CANCEL_IT = "❌ Cancel"

    # up_helper.py

    TRY_UP = """
**Uploading {}… Please wait**

    """

    CANT_FIND = "Sorry ! I can't find that file {} 💀"

    TOO_LARGE = "URL file is too large to send in telegram 😥"

    ARCHIVE_GONE = "Archive has gone from servers before uploading 😥"

    EMPTY_FILE = "The file {} is empty/unreachable"

    CHECK_MSG = """
**Verifying the file… Please wait**

    """


# List of error messages from p7zip
ERROR_MSGS = ["Error", "Can't open as archive"]


# Inline buttons
class Buttons:
    START_BUTTON = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(Messages.HELP, callback_data="helpcallback"),
                InlineKeyboardButton(Messages.ABOUT, callback_data="aboutcallback"),
            ],
            [
                InlineKeyboardButton(Messages.STATS_BTN, callback_data="statscallback"),
                InlineKeyboardButton(Messages.DONATE, callback_data="donatecallback"),
            ],
        ]
    )

    REFRESH_BUTTON = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    Messages.REFRESH, callback_data="statscallback|refresh"
                ),
                InlineKeyboardButton(Messages.BACK, callback_data="megoinhome"),
            ]
        ]
    )

    CHOOSE_E_F__BTNS = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🗂️", callback_data="extract_file|tg_file|no_pass"),
                InlineKeyboardButton(
                    "🔐", callback_data="extract_file|tg_file|with_pass"
                ),
            ],
            [
                InlineKeyboardButton("🖼️", callback_data="extract_file|tg_file|thumb"),
                InlineKeyboardButton(
                    "✏", callback_data="extract_file|tg_file|thumbrename"
                ),
            ],
            [InlineKeyboardButton("❌", callback_data="cancel_dis")],
        ]
    )

    CHOOSE_E_F_M__BTNS = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🗂️", callback_data="merged|no_pass"),
                InlineKeyboardButton("🔐", callback_data="merged|with_pass"),
            ],
            [InlineKeyboardButton("❌", callback_data="cancel_dis")],
        ]
    )

    CHOOSE_E_U__BTNS = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🔗", callback_data="extract_file|url|no_pass"),
                InlineKeyboardButton("🔐", callback_data="extract_file|url|with_pass"),
            ],
            [
                InlineKeyboardButton("🖼️", callback_data="extract_file|url|thumb"),
                InlineKeyboardButton("✏", callback_data="extract_file|url|thumbrename"),
            ],
            [InlineKeyboardButton("❌", callback_data="cancel_dis")],
        ]
    )

    RENAME = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("✏", callback_data="renameit"),
                InlineKeyboardButton("🙅‍♂️", callback_data="norename"),
            ]
        ]
    )

    CLN_BTNS = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(Messages.CLEAN, callback_data="cancel_dis"),
                InlineKeyboardButton(Messages.CANCEL_IT, callback_data="nobully"),
            ]
        ]
    )

    ME_GOIN_HOME = InlineKeyboardMarkup(
        [[InlineKeyboardButton(Messages.BACK, callback_data="megoinhome")]]
    )

    SET_UPLOAD_MODE_BUTTONS = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(Messages.AS_DOC, callback_data="set_mode|doc"),
                InlineKeyboardButton(Messages.AS_MEDIA, callback_data="set_mode|media"),
            ],
        ]
    )

    I_PREFER_STOP = InlineKeyboardMarkup(
        [[InlineKeyboardButton(Messages.CANCEL_IT, callback_data="canceldownload")]]
    )

    MERGE_THEM_ALL = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(Messages.MERGE_BTN, callback_data="merge_this"),
                InlineKeyboardButton(Messages.CANCEL_IT, callback_data="cancel_dis"),
            ]
        ]
    )

    THUMB_REPLACEMENT = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(Messages.CHECK, callback_data="check_thumb"),
                InlineKeyboardButton(
                    Messages.REPLACE, callback_data="save_thumb|replace"
                ),
            ],
            [InlineKeyboardButton(Messages.CANCEL_IT, callback_data="nope_thumb")],
        ]
    )

    THUMB_FINAL = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    Messages.REPLACE, callback_data="save_thumb|replace"
                ),
                InlineKeyboardButton(Messages.CANCEL_IT, callback_data="nope_thumb"),
            ]
        ]
    )

    THUMB_SAVE = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(Messages.SAVE, callback_data="save_thumb|save"),
                InlineKeyboardButton(Messages.CANCEL_IT, callback_data="nope_thumb"),
            ]
        ]
    )

    THUMB_DEL = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(Messages.CHECK, callback_data="check_before_del"),
                InlineKeyboardButton(Messages.DELETE, callback_data="del_thumb"),
            ],
            [InlineKeyboardButton(Messages.CANCEL_IT, callback_data="nope_thumb")],
        ]
    )

    THUMB_DEL_2 = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(Messages.DELETE, callback_data="del_thumb"),
                InlineKeyboardButton(Messages.CANCEL_IT, callback_data="nope_thumb"),
            ],
        ]
    )

    RATE_ME = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    Messages.RATE, url="https://t.me/BotsArchive/2705"
                ),
                InlineKeyboardButton(Messages.DONATE, callback_data="donatecallback"),
            ],
        ]
    )
