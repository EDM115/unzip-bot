# Copyright (c) 2023 EDM115
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# Inline buttons
class Buttons:
    START_BUTTON = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Help 📜", callback_data="helpcallback"),
                InlineKeyboardButton("About 👀", callback_data="aboutcallback"),
            ],
            [
                InlineKeyboardButton("Stats 📊", callback_data="statscallback"),
                InlineKeyboardButton("💸 Donate", callback_data="donatecallback"),
            ]
        ]
    )

    REFRESH_BUTTON = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Refresh ♻️", callback_data="statscallback|refresh"),
                InlineKeyboardButton("Back 🏡", callback_data="megoinhome"),
            ]
        ]
    )

    CHOOSE_E_F__BTNS = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🗂️", callback_data="extract_file|tg_file|no_pass"
                ),
                InlineKeyboardButton(
                    "🔐", callback_data="extract_file|tg_file|with_pass"
                ),
            ],
            [
                InlineKeyboardButton("🖼️", callback_data="extract_file|tg_file|thumb"),
                InlineKeyboardButton(
                    "🖼️✏", callback_data="extract_file|tg_file|thumbrename"
                ),
            ],
            [InlineKeyboardButton("❌", callback_data="cancel_dis")],
        ]
    )

    CHOOSE_E_F_M__BTNS = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🗂️", callback_data="merged|no_pass"
                ),
                InlineKeyboardButton(
                    "🔐", callback_data="merged|with_pass"
                ),
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
                InlineKeyboardButton(
                    "🖼️✏", callback_data="extract_file|url|thumbrename"
                ),
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
                InlineKeyboardButton("Clean my files 🚮", callback_data="cancel_dis"),
                InlineKeyboardButton("❌ Cancel", callback_data="nobully"),
            ]
        ]
    )

    ME_GOIN_HOME = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Back 🏡", callback_data="megoinhome")]]
    )

    SET_UPLOAD_MODE_BUTTONS = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("As document 📁", callback_data="set_mode|doc"),
                InlineKeyboardButton("As media 📺", callback_data="set_mode|media")
            ],
        ]
    )

    I_PREFER_STOP = InlineKeyboardMarkup(
        [[InlineKeyboardButton("❌ Cancel", callback_data="canceldownload")]]
    )

    MERGE_THEM_ALL = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Merge 🛠️", callback_data="merge_this"),
                InlineKeyboardButton("❌ Cancel", callback_data="cancel_dis"),
            ]
        ]
    )

    THUMB_REPLACEMENT = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Check 👀", callback_data="check_thumb"),
                InlineKeyboardButton("Replace ⏭", callback_data="save_thumb|replace"),
            ],
            [InlineKeyboardButton("❌ Cancel", callback_data="nope_thumb")],
        ]
    )

    THUMB_FINAL = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Replace ⏭", callback_data="save_thumb|replace"),
                InlineKeyboardButton("❌ Cancel", callback_data="nope_thumb"),
            ]
        ]
    )

    THUMB_SAVE = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Save 💾", callback_data="save_thumb|save"),
                InlineKeyboardButton("❌ Cancel", callback_data="nope_thumb"),
            ]
        ]
    )

    THUMB_DEL = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Check 👀", callback_data="check_before_del"),
                InlineKeyboardButton("Delete 🚮", callback_data="del_thumb"),
            ],
            [InlineKeyboardButton("❌ Cancel", callback_data="nope_thumb")],
        ]
    )

    THUMB_DEL_2 = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Delete 🚮", callback_data="del_thumb"),
                InlineKeyboardButton("❌ Cancel", callback_data="nope_thumb")
            ],
        ]
    )

    RATE_ME = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("⭐ Rate me", url="https://t.me/BotsArchive/2705"),
                InlineKeyboardButton("💸 Donate", callback_data="donatecallback")
            ],
        ]
    )

class Messages:
    START_TEXT = """
Hi **{}** 👋, I'm **Unarchiver bot** 🥰


I can extract archives like `zip`, `rar`, `tar`, …

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
    **2.** Please don’t send corrupted files ! If you sent one by mistake just send **/clean**
    **3.** If your archive have +95 files in it then bot can’t show all of extracted files to select from (yet). So in that case if you can’t see your file in the buttons just click on `Upload all 📤` button. It will send all extracted files to you !


**• Got an error ?**
    Visit edm115.eu.org/unzip#help


**• I wanna have help 🥺**

    PM me at **@EDM115** or join the chat **@EDM115_chat**
    """

    ABOUT_TXT = """
**About Unarchiver bot [v6.1.1]**

• **Language :** [Python 3.11.3](https://www.python.org/)
• **Framework :** [Pyrogram 2.0.106](https://pyrogram.org/)
• **Source code :** [EDM115/unzip-bot](https://github.com/EDM115/unzip-bot/tree/beta)
• **Developer :** [EDM115](https://github.com/EDM115)

**[Rate me ⭐](https://t.me/BotsArchive/2705)**
Made with ❤️ by **@EDM115bots**
    """

    DONATE_TEXT = """
I'm going to be honest : **this bot costs me money**...
Nothing's free on this world, however I try to keep this bot for free for as many people as possible
I don't like to put restrictions, nor getting your PM's flooded with ads...

So if you can, donate :)
It helps out a ton, covers the costs (hosting, updating, ... 👨‍💻)

__How ?__
• **[Paypal](https://www.paypal.me/8EDM115)**
• **[GitHub Sponsors](https://github.com/sponsors/EDM115)**
• **[Directly in Telegram](https://t.me/EDM115bots/170)**
• **[BuyMeACoffee](https://www.buymeacoffee.com/edm115)**
• **[Send cryptos (not recommended)](https://edm115.shadd.eu.org/)**

Thanks for your contribution 😊
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

    CHOOSE_EXT_MODE = """
Select the extraction mode for that {} 👀

{} : **Normal mode**
🔐 : **Password protected**
🖼️ : **Change the thumbnail**
🖼️✏ : **Change the thumbnail and rename the file**
❌ : **Cancel your task**
    """

    CHOOSE_EXT_MODE_MERGE = """
Select the extraction mode for that merged file 👀

🗂️ : **Normal mode**
🔐 : **Password protected**
❌ : **Cancel your task**
    """

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

    EXT_CAPTION = """
`{}`

Successfully extracted by @unzip_edm115bot 🥰
    """

    URL_UPLOAD = """
`{}` is too huge to be uploaded to Telegram (`{}`)

Instead, I made it available here : {} 🥰
    """

    URL_ERROR = """
An error happened for `{}` 😕

**Error code :** `{}`
**Error type :** `{}`
**Error message :** `{}`

Please report this at @EDM115 if you think this is a serious error
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

    START_TXT = """
ℹ️ The bot have successfully started at `{}` 💪
    """

    STOP_TXT = """
ℹ️ The bot goes sleeping at `{}` 😴
    """

    EXT_FAILED_TXT = """
**Extraction failed 😕**

**What to do ?**

   • **If you sent splitted archives (.001, .part1, .00001, …), then I can’t extract them 🙂** (for the moment)
   • Please make sure archive isn’t corrupted
   • Please make sure that you selected the right mode !
   • Also check if you sent the right password (it's case sensitive)
   • Maybe your archive format isn’t supported yet 😔


**⚠ IN ALL CASES ⚠**, please send **/clean**, else you couldn’t send any other task 🙂🔫 (may be fixed in the future)

Please report this at @EDM115 if you think this is a serious error
    """

    ERROR_TXT = """
**Error happened 😕**

`{}`

Please report this at @EDM115 if you think this is a serious error
    """

    CANCELLED_TXT = """
**{} ✅**
    """

    DL_STOPPED = """
✅ The download of your file have successfully been cancelled 😌
    """

    HOW_MANY_UPLOADED = """
`{}` files were extracted from that archive
    """

    CLEAN_TXT = """
**Are sure want to clean your task 🤔**

Note : This action cannot be undone !
    """

    SELECT_UPLOAD_MODE_TXT = """
Select your upload mode 👇

**Current upload mode is :** `{}`
    """

    CHANGED_UPLOAD_MODE_TXT = """
**Successfully changed upload mode to** `{}` ✅
    """

    EXISTING_THUMB = """
A thumbnail already have been saved 😅 What you wanna do ?
• Checking the actual thumbnail
• Replace it with the new one you just sent
• Cancel
    """

    SAVING_THUMB = """
Are you sure you want to save this thumbnail 🤔
    """

    SAVED_THUMBNAIL = """
**Successfully saved this thumbnail ✅**
    """

    DEL_CONFIRM_THUMB = """
Do you really want to delete your thumbnail ?
• Check the actual thumbnail
• Delete it
• Cancel
"""

    DEL_CONFIRM_THUMB_2 = """
Do you really want to delete your thumbnail ?
"""

    DELETED_THUMB = """
**Successfully removed your thumbnail ✅**
    """

    PLS_REPLY = """
You need to reply to a picture for saving it as custom thumbnail 🤓
    """

    NO_MERGE_TASK = """
Bruh there's no merge task ongoing 🗿
Use **/merge** to start one
    """

# List of error messages from p7zip
ERROR_MSGS = ["Error", "Can't open as archive"]
