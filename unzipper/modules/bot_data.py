# Copyright (c) 2022 EDM115

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Inline buttons
class Buttons:
    START_BUTTON = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Help 📜", callback_data="helpcallback"),
                InlineKeyboardButton("About 🧐", callback_data="aboutcallback")
            ]
        ])
    
    CHOOSE_E_F__BTNS = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🗂️ File extract", callback_data="extract_file|tg_file|no_pass"),
            ],
            [
                InlineKeyboardButton("🗂️ Extract a password protected archive 🔐", callback_data="extract_file|tg_file|with_pass")
            ],
            [
                InlineKeyboardButton("❌ Cancel", callback_data="cancel_dis")
            ]
        ])

    CHOOSE_E_U__BTNS = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔗 URL extract", callback_data="extract_file|url|no_pass"),
            ],
            [
                InlineKeyboardButton("🔗 URL extract (but password protected) 🔐", callback_data="extract_file|url|with_pass")
            ],
            [
                InlineKeyboardButton("❌ Cancel", callback_data="cancel_dis")
            ]
        ])

    CLN_BTNS = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Clean my files 🚮", callback_data="cancel_dis")
            ],
            [
                InlineKeyboardButton("Noooo 😅", callback_data="nobully")
            ]
        ])
    
    ME_GOIN_HOME = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Back 🏡", callback_data="megoinhome")
            ]
        ])

class Messages:
    START_TEXT = """
Hi **{}** 👋, I'm **Unarchiver Bot** 🥰
`This is Personal Use Only version !`

I can extract archives like zip, rar, tar, …

**Made with ❤️ by @EDM115bots**
    """

    HELP_TXT = """
**• How to extract 🤔**

  **1)** Send the file or link that you want to extract
  **2)** Click on extract button (If you sent a link use `🔗 URL extract` button. If it's a file just use `🗂️ File extract` button)

**Note:**
  **1.** If your archive is password protected select `🗂️ Extract a password protected archive 🔐` mode. Bot isn’t a god to know your file’s password, so if this happens just send that password !
  
  **2.** Please don’t send corrupted files ! If you sent a one by mistake just send **/clean** command
  
  **3.** If your archive have +95 files in it then bot can’t show all of extracted files to select from. So in that case if you can’t see your file in the buttons just click on `Upload all 📤` button. It’ll send all extracted files to you !

**• I wanna have help 🥺**

  PM me at **@EDM115**, I'm always here and open for anything 😘
    """

    ABOUT_TXT = """
**About Unarchiver Bot [PERSONAL USE ONLY]**

• **Language :** [Python](https://www.python.org/)
• **Framework :** [Pyrogram](https://docs.pyrogram.org/)
• **Source code :** [EDM115/unzip-bot](https://github.com/EDM115/unzip-bot/tree/personal_only)
• **Developer :** [EDM115](https://github.com/EDM115)


**Made with ❤️ by @EDM115bots**
    """

    AFTER_OK_DL_TXT = """
**Successfully downloaded ✅**

**Download time :** `{}`
**Status :** Trying to extract the archive… Please wait
    """

    EXT_OK_TXT = """
**Extraction successfull ✅**

**Extraction time :** `{}`
**Status :** Trying to upload… Please wait
    """

    EXT_CAPTION = """
`{}`

Successfully extracted by @unzip_edm115bot 🥰
    """

    EXT_FAILED_TXT = """
**Extraction Failed 😕**

**What to do ?**

 • Please make sure archive isn’t corrupted
 • Please make sure that you selected the right mode!
 • Also check if you sent the right password (it's case sensitive)
 • Maybe your archive format isn’t supported yet 😔
 • If you sent splitted archives (.001, .part1, .00001, …), then I can’t extract them 🙂

**IN ALL CASES**, please send **/clean**, else you couldn’t send any other task 🙂🔫

**Please report this at @EDM115 if you think this is a serious error**
    """

    ERROR_TXT = """
**Error Happened 😕**

**ERROR:** `{}`

**Please report this at @EDM115 if you think this is a serious error**
    """

    CANCELLED_TXT = """
**{} ✅**

Now all of your files have been deleted from my server 😌
    """

    CLEAN_TXT = """
**Are sure want to delete your files from my server 🤔**

**Note : This action cannot be undone !**
    """

# List of error messages from p7zip
ERROR_MSGS = [
    "Error",
    "Can't open as archive"
    ]
