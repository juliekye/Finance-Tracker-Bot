import os
import pgpy
import telegram

from pgpy import PGPMessage
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

from shared.handlers import CHandler

# Import environment variables
from env import GREETINGS_MESSAGE, CANCEL_TEXT, SUCCESS_MESSAGE, ERROR_MESSAGE, DECRIPTION_SUCCESSFUL_MESSAGE, PGP_PASSPHRASE, PGP_DIR, logger


class TwoFABot:
    def __init__(self, token: str):
        self.c_handler = CHandler()
        self._token = token
        self._updater: Updater = None
        self._dp: Updater.dispatcher = None
        self.bot: telegram.Bot = None

    def run(self):
        self._updater = Updater(self._token)
        self._dp = self._updater.dispatcher
        self.bot = self._updater.bot

        self._dp.add_handler(CommandHandler("start", self.bot_startup))
        self._dp.add_handler(MessageHandler(Filters.text, self.process_text))

        self._updater.start_polling()

    def bot_startup(self, update: Update, context: CallbackContext):
        """Handles /start command"""
        message = update.message
        chat_id = message.chat.id

        logger.info(f'TWOFA_bot.py:bot_startup(). /start from [id={chat_id}]')

        try:
            self.bot.send_message(chat_id, GREETINGS_MESSAGE)
        except Exception as e:
            logger.error(f'TWOFA_bot.py:bot_startup(). Exception: {e}')

    def process_text(self, update: Update, context: CallbackContext):
        """Decrypts a pgp signed message"""
        message = update.message
        chat_id = message.chat.id

        if self.c_handler.has_callback(message.chat.id) and not message.text == CANCEL_TEXT:
            self.c_handler.get_callback(message.chat.id)(message)
            return

        if message.text == CANCEL_TEXT:
            self.bot.send_message(chat_id, SUCCESS_MESSAGE)
        else:
            try:
                self.decrypt_message(chat_id, message.text)
            except:
                self.bot.send_message(chat_id, ERROR_MESSAGE)

    def decrypt_message(self, chat_id: int, text: str):
        try:
            key, _ = pgpy.PGPKey.from_file(os.path.join(PGP_DIR, 'key.asc'))
            message = PGPMessage.from_blob(text)

            with key.unlock(PGP_PASSPHRASE):
                result = key.decrypt(message).message
                if isinstance(result, bytes):
                    result = result.decode('utf-8')
                self.bot.send_message(chat_id, DECRIPTION_SUCCESSFUL_MESSAGE)
                self.bot.send_message(chat_id, '<code>' + result + '</code>', parse_mode=telegram.ParseMode.HTML)
        except Exception as e:
            logger.error('TWOFA_bot.py:decrypt_message(). Error dycrypting the following message:\n' + text + f'. Exception: {e}')
