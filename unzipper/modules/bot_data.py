# Copyright (c) 2022 EDM115

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Inline buttons
class Buttons:
    START_BUTTON = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Help 📜", callback_data="helpcallback"),
                InlineKeyboardButton("About 👀", callback_data="aboutcallback")
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
                )
            ],
            [
                InlineKeyboardButton(
                    "🖼️", callback_data="extract_file|tg_file|thumb"
                ),
                InlineKeyboardButton(
                    "🖼️✏", callback_data="extract_file|tg_file|thumbrename"
                )
            ],
            [
                InlineKeyboardButton("❌", callback_data="cancel_dis")
            ]
        ]
    )

    CHOOSE_E_U__BTNS = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🔗", callback_data="extract_file|url|no_pass"),
                InlineKeyboardButton("🔐", callback_data="extract_file|url|with_pass")
            ],
            [
                InlineKeyboardButton(
                    "🖼️", callback_data="extract_file|url|thumb"
                ),
               InlineKeyboardButton(
                    "🖼️✏", callback_data="extract_file|url|thumbrename"
                )
            ],
            [
                InlineKeyboardButton("❌", callback_data="cancel_dis")
            ]
        ]
    )
    
    RENAME = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("✏", callback_data="renameit"),
                InlineKeyboardButton("🙅‍♂️", callback_data="norename")
            ]
        ]
    )

    CLN_BTNS = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Clean my files 🚮", callback_data="cancel_dis"),
                InlineKeyboardButton("❌ Cancel", callback_data="nobully")
            ]
        ]
    )

    ME_GOIN_HOME = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Back 🏡", callback_data="megoinhome")]]
    )

    SET_UPLOAD_MODE_BUTTONS = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("As document 📁", callback_data="set_mode|doc")],
            [InlineKeyboardButton("As media 📺", callback_data="set_mode|media")]
        ]
    )

    I_PREFER_STOP = InlineKeyboardMarkup(
        [[InlineKeyboardButton("❌ Cancel", callback_data="canceldownload")]]
    )

    MERGE_THEM_ALL = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Merge 🛠️", callback_data="merge_this"),
                InlineKeyboardButton("❌ Cancel", callback_data="nobully")
            ]
        ]
    )

    THUMB_REPLACEMENT = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Check 👀", callback_data="check_thumb"),
                InlineKeyboardButton("Replace ⏭", callback_data="save_thumb|replace")
            ],
            [InlineKeyboardButton("❌ Cancel", callback_data="nope_thumb")]
        ]
    )

    THUMB_FINAL = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Replace ⏭", callback_data="save_thumb|replace"),
                InlineKeyboardButton("❌ Cancel", callback_data="nope_thumb")
            ]
        ]
    )

    THUMB_SAVE = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Save 💾", callback_data="save_thumb|save"),
                InlineKeyboardButton("❌ Cancel", callback_data="nope_thumb")
            ]
        ]
    )


class Messages:
    START_TEXT = """
Hi **{}** 👋, I'm **Unarchiver bot** 🥰

I can extract archives like `zip`, `rar`, `tar`, …

**Made with ❤️ by @EDM115bots**
    """
    # **This is BETA version !** May be a lot buggy, but with new features. Better waiting for the stable version at daytime… 🙂

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


**• I wanna have help 🥺**

    PM me at **@EDM115**
    """

    ABOUT_TXT = """
**About Unarchiver bot [BETA | v5.0.3]**

• **Language :** [Python 3.10.6](https://www.python.org/)
• **Framework :** [Pyrogram 2.0.41](https://docs.pyrogram.org/)
• **Source code :** [EDM115/unzip-bot](https://github.com/EDM115/unzip-bot/tree/beta)
• **Developer :** [EDM115](https://github.com/EDM115)

**Made with ❤️ by @EDM115bots**
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

    AFTER_OK_DL_TXT = """
**Successfully downloaded ✅**

**Download time :** `{}`
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

   • Please make sure archive isn’t corrupted
   • Please make sure that you selected the right mode !
   • Also check if you sent the right password (it's case sensitive)
   • Maybe your archive format isn’t supported yet 😔
   • **If you sent splitted archives (.001, .part1, .00001, …), then I can’t extract them 🙂** (for the moment)


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

    DELETED_THUMB = """
**Successfully removed your thumbnail ✅**
    """

    PLS_REPLY = """
You need to reply to a picture for saving it as custom thumbnail 🤓
    """


# List of error messages from p7zip
ERROR_MSGS = ["Error", "Can't open as archive"]
