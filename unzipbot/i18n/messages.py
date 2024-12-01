import json

from config import Config


class Messages:
    def __init__(
        self,
        lang_fetcher=None,
        default_lang=Config.BASE_LANGUAGE,
        base_path="unzipbot/i18n/lang",
    ):
        """
        Initialize the Messages class.

        :param lang_fetcher: A callable to fetch the user's language (takes user_id as argument).
        :param default_lang: The default language code (e.g., "en").
        :param base_path: The base path to the directory containing language files.
        """
        self.lang_fetcher = lang_fetcher or (lambda _: default_lang)
        self.default_lang = default_lang
        self.base_path = base_path

    def __load_language_file(self, lang):
        """
        Load the JSON file for the given language.

        :param lang: Language code (e.g., "en").
        :return: Dictionary of messages.
        """
        file_path = f"{self.base_path}/{lang}.json"

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            with open(
                f"{self.base_path}/{self.default_lang}.json", "r", encoding="utf-8"
            ) as f:
                return json.load(f)

    def get(self, file, key, user_id=None, *args, **kwargs):
        """
        Retrieve and format a message by its file and key.

        :param file: The name of the file in the JSON structure.
        :param key: The key within the file to retrieve.
        :param user_id: The user's ID (used to fetch the preferred language).
        :param args: Positional arguments for string formatting.
        :param kwargs: Keyword arguments for string formatting.
        :return: The formatted message string.
        """
        lang = self.lang_fetcher(user_id) if user_id else self.default_lang
        messages = self.__load_language_file(lang)

        try:
            message = messages[file][key.lower()]
        except KeyError:
            message = self.__load_language_file(self.default_lang)[file][key.lower()]

        return message.format(*args, **kwargs)
