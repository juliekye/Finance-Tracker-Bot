import os

from logging import Logger
from shared.logger import get_logger
from shared.shared_env import *


# Define constants
PGP_DIR: str = os.path.join(BASE_DIR, 'PGP')

CANCEL_TEXT: str = '❌ Cancel'
ERROR_MESSAGE: str = '❌ An error has occured!'
SUCCESS_MESSAGE: str = '✅ Done!'
DECRIPTION_SUCCESSFUL_MESSAGE: str = '😎 The message has been decrypted!'
GREETINGS_MESSAGE: str = '👋 Send an encrypted PGP message to the bot!'

# Create a logger
logger: Logger = get_logger(__name__, os.path.join(BASE_DIR, 'logs/two_fa_bot.log'))
