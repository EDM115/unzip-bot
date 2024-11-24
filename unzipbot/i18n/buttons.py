from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from .messages import Messages
from unzipbot.helpers.database import get_lang


messages = Messages(lang_fetcher=get_lang)


# Inline buttons
class Buttons:
    START_BUTTON = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    messages.get("buttons", "HELP"), callback_data="helpcallback"
                ),
                InlineKeyboardButton(
                    messages.get("buttons", "ABOUT"), callback_data="aboutcallback"
                ),
            ],
            [
                InlineKeyboardButton(
                    messages.get("buttons", "STATS_BTN"), callback_data="statscallback"
                ),
                InlineKeyboardButton(
                    messages.get("buttons", "DONATE"), callback_data="donatecallback"
                ),
            ],
        ]
    )

    REFRESH_BUTTON = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    messages.get("buttons", "REFRESH"),
                    callback_data="statscallback|refresh",
                ),
                InlineKeyboardButton(
                    messages.get("buttons", "BACK"), callback_data="megoinhome"
                ),
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
                InlineKeyboardButton(
                    messages.get("buttons", "CLEAN"), callback_data="cancel_dis"
                ),
                InlineKeyboardButton(
                    messages.get("buttons", "CANCEL_IT"), callback_data="nobully"
                ),
            ]
        ]
    )

    ME_GOIN_HOME = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    messages.get("buttons", "BACK"), callback_data="megoinhome"
                )
            ]
        ]
    )

    SET_UPLOAD_MODE_BUTTONS = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    messages.get("buttons", "AS_DOC"), callback_data="set_mode|doc"
                ),
                InlineKeyboardButton(
                    messages.get("buttons", "AS_MEDIA"), callback_data="set_mode|media"
                ),
            ],
        ]
    )

    I_PREFER_STOP = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    messages.get("buttons", "CANCEL_IT"), callback_data="canceldownload"
                )
            ]
        ]
    )

    MERGE_THEM_ALL = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    messages.get("buttons", "MERGE_BTN"), callback_data="merge_this"
                ),
                InlineKeyboardButton(
                    messages.get("buttons", "CANCEL_IT"), callback_data="cancel_dis"
                ),
            ]
        ]
    )

    THUMB_REPLACEMENT = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    messages.get("buttons", "CHECK"), callback_data="check_thumb"
                ),
                InlineKeyboardButton(
                    messages.get("buttons", "REPLACE"),
                    callback_data="save_thumb|replace",
                ),
            ],
            [
                InlineKeyboardButton(
                    messages.get("buttons", "CANCEL_IT"), callback_data="nope_thumb"
                )
            ],
        ]
    )

    THUMB_FINAL = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    messages.get("buttons", "REPLACE"),
                    callback_data="save_thumb|replace",
                ),
                InlineKeyboardButton(
                    messages.get("buttons", "CANCEL_IT"), callback_data="nope_thumb"
                ),
            ]
        ]
    )

    THUMB_SAVE = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    messages.get("buttons", "SAVE"), callback_data="save_thumb|save"
                ),
                InlineKeyboardButton(
                    messages.get("buttons", "CANCEL_IT"), callback_data="nope_thumb"
                ),
            ]
        ]
    )

    THUMB_DEL = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    messages.get("buttons", "CHECK"), callback_data="check_before_del"
                ),
                InlineKeyboardButton(
                    messages.get("buttons", "DELETE"), callback_data="del_thumb"
                ),
            ],
            [
                InlineKeyboardButton(
                    messages.get("buttons", "CANCEL_IT"), callback_data="nope_thumb"
                )
            ],
        ]
    )

    THUMB_DEL_2 = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    messages.get("buttons", "DELETE"), callback_data="del_thumb"
                ),
                InlineKeyboardButton(
                    messages.get("buttons", "CANCEL_IT"), callback_data="nope_thumb"
                ),
            ],
        ]
    )

    RATE_ME = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    messages.get("buttons", "RATE"), url="https://t.me/BotsArchive/2705"
                ),
                InlineKeyboardButton(
                    messages.get("buttons", "DONATE"), callback_data="donatecallback"
                ),
            ],
        ]
    )
