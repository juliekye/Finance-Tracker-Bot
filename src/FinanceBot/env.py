from logging import Logger
import logging
from logging.handlers import RotatingFileHandler
from shared.logger import get_logger
from shared.shared_env import *


# Define constants
FINANCE_INFO_FILE: str = os.path.join(BASE_DIR, 'data/finance_info.json')
LOG_FILE_PATH: str = os.path.join(BASE_DIR, 'logs/finance_bot.log')
FINANCIAL_ACTIVITY_LOG_FILE_PATH: str = os.path.join(BASE_DIR, 'logs/financial_activity.log')


SUCCESS_TEXT: str = '✅ Done!'
ERROR_TEXT: str = '🚫 Error has occured!'
CANCEL_TEXT: str = '❌ Cancel'
GREETING_TEXT: str = '👋 Welcome to the financial bot %s!'
PROFITS_TEXT: str = '₿ Profits'
LEND_MONEY_TEXT: str = '🏦 New loan'
BALANCE_CHANGE_TEXT: str = '🦍 New income/expenditure'
GET_LOGS_TEXT: str = '⬆️ Download logs'
REQUEST_BALANCE_CHANGE_TEXT: str = '🔥 Enter balance change:'
REQUEST_BALANCE_CHANGE_COMMENT_TEXT: str = '✉️ Enter explanation:'
LOAN_NOT_IMPLEMENTED_ERROR_TEXT: str = '😢 Bot can only handle 2 users for now...'
CHOOSE_LOAN_LENDER_TEXT: str = '🥸 Choose a user to be a lender:'
WRONG_LOAN_AMMOUNT_TEXT: str = '💸 Loan amount can\'t be less than $5!'
ENTER_LOAN_AMOUNT_TEXT: str = '🤔 How much do you want to lend? <i>(min $5)</i>'
WRONG_SYNTAX_TEXT: str = '💩 Syntax error!'
HELPER_TEXT: str = '''🗣 <b>Bot's commands:</b>

/start 

/set_profits user amount <i># Set profits for the user</i>

/set_spent user amount <i># Set expenditures of the user</i>'''


# Create a logger
logger: Logger = get_logger(__name__, LOG_FILE_PATH)

# Create action logger (It is used to save financial activity). It is capped at 125 MB
action_logger: Logger = get_logger('action_logger', log_file_path=FINANCIAL_ACTIVITY_LOG_FILE_PATH, max_file_size=125*1024*1024, backupCount=4)
