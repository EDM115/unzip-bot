from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from unzipbot.helpers.database import get_lang

from .messages import Messages

messages = Messages(lang_fetcher=get_lang)


# Inline buttons
class Buttons:
    START_BUTTON = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=messages.get(file="buttons", key="HELP"),
                    callback_data="helpcallback",
                ),
                InlineKeyboardButton(
                    text=messages.get(file="buttons", key="ABOUT"),
                    callback_data="aboutcallback",
                ),
            ],
            [
                InlineKeyboardButton(
                    text=messages.get(file="buttons", key="STATS_BTN"),
                    callback_data="statscallback",
                ),
                InlineKeyboardButton(
                    text=messages.get(file="buttons", key="DONATE"),
                    callback_data="donatecallback",
                ),
            ],
        ]
    )

    REFRESH_BUTTON = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=messages.get(file="buttons", key="REFRESH"),
                    callback_data="statscallback|refresh",
                ),
                InlineKeyboardButton(
                    text=messages.get(file="buttons", key="BACK"),
                    callback_data="megoinhome",
                ),
            ]
        ]
    )

    CHOOSE_E_F__BTNS = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="🗂️", callback_data="extract_file|tg_file|no_pass"
                ),
                InlineKeyboardButton(
                    text="🔐", callback_data="extract_file|tg_file|with_pass"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🖼️", callback_data="extract_file|tg_file|thumb"
                ),
                InlineKeyboardButton(
                    text="✏", callback_data="extract_file|tg_file|thumbrename"
                ),
            ],
            [InlineKeyboardButton(text="❌", callback_data="cancel_dis")],
        ]
    )

    CHOOSE_E_F_M__BTNS = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text="🗂️", callback_data="merged|no_pass"),
                InlineKeyboardButton(text="🔐", callback_data="merged|with_pass"),
            ],
            [InlineKeyboardButton(text="❌", callback_data="cancel_dis")],
        ]
    )

    CHOOSE_E_U__BTNS = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="🔗", callback_data="extract_file|url|no_pass"
                ),
                InlineKeyboardButton(
                    text="🔐", callback_data="extract_file|url|with_pass"
                ),
            ],
            [
                InlineKeyboardButton(text="🖼️", callback_data="extract_file|url|thumb"),
                InlineKeyboardButton(
                    text="✏", callback_data="extract_file|url|thumbrename"
                ),
            ],
            [InlineKeyboardButton(text="❌", callback_data="cancel_dis")],
        ]
    )

    RENAME = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text="✏", callback_data="renameit"),
                InlineKeyboardButton(text="🙅‍♂️", callback_data="norename"),
            ]
        ]
    )

    CLN_BTNS = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=messages.get(file="buttons", key="CLEAN"),
                    callback_data="cancel_dis",
                ),
                InlineKeyboardButton(
                    text=messages.get(file="buttons", key="CANCEL_IT"),
                    callback_data="nobully",
                ),
            ]
        ]
    )

    ME_GOIN_HOME = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=messages.get(file="buttons", key="BACK"),
                    callback_data="megoinhome",
                )
            ]
        ]
    )

    SET_UPLOAD_MODE_BUTTONS = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=messages.get(file="buttons", key="AS_DOC"),
                    callback_data="set_mode|doc",
                ),
                InlineKeyboardButton(
                    text=messages.get(file="buttons", key="AS_MEDIA"),
                    callback_data="set_mode|media",
                ),
            ]
        ]
    )

    I_PREFER_STOP = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=messages.get(file="buttons", key="CANCEL_IT"),
                    callback_data="canceldownload",
                )
            ]
        ]
    )

    MERGE_THEM_ALL = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=messages.get(file="buttons", key="MERGE_BTN"),
                    callback_data="merge_this",
                ),
                InlineKeyboardButton(
                    text=messages.get(file="buttons", key="CANCEL_IT"),
                    callback_data="cancel_dis",
                ),
            ]
        ]
    )

    THUMB_REPLACEMENT = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=messages.get(file="buttons", key="CHECK"),
                    callback_data="check_thumb",
                ),
                InlineKeyboardButton(
                    text=messages.get(file="buttons", key="REPLACE"),
                    callback_data="save_thumb|replace",
                ),
            ],
            [
                InlineKeyboardButton(
                    text=messages.get(file="buttons", key="CANCEL_IT"),
                    callback_data="nope_thumb",
                )
            ],
        ]
    )

    THUMB_FINAL = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=messages.get(file="buttons", key="REPLACE"),
                    callback_data="save_thumb|replace",
                ),
                InlineKeyboardButton(
                    text=messages.get(file="buttons", key="CANCEL_IT"),
                    callback_data="nope_thumb",
                ),
            ]
        ]
    )

    THUMB_SAVE = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=messages.get(file="buttons", key="SAVE"),
                    callback_data="save_thumb|save",
                ),
                InlineKeyboardButton(
                    text=messages.get(file="buttons", key="CANCEL_IT"),
                    callback_data="nope_thumb",
                ),
            ]
        ]
    )

    THUMB_DEL = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=messages.get(file="buttons", key="CHECK"),
                    callback_data="check_before_del",
                ),
                InlineKeyboardButton(
                    text=messages.get(file="buttons", key="DELETE"),
                    callback_data="del_thumb",
                ),
            ],
            [
                InlineKeyboardButton(
                    text=messages.get(file="buttons", key="CANCEL_IT"),
                    callback_data="nope_thumb",
                )
            ],
        ]
    )

    THUMB_DEL_2 = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=messages.get(file="buttons", key="DELETE"),
                    callback_data="del_thumb",
                ),
                InlineKeyboardButton(
                    text=messages.get(file="buttons", key="CANCEL_IT"),
                    callback_data="nope_thumb",
                ),
            ]
        ]
    )

    RATE_ME = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=messages.get(file="buttons", key="RATE"),
                    url="https://t.me/BotsArchive/2705",
                ),
                InlineKeyboardButton(
                    text=messages.get(file="buttons", key="DONATE"),
                    callback_data="donatecallback",
                ),
            ]
        ]
    )
