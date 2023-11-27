import re
import telegram

from contextlib import suppress
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyMarkup, Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import CommandHandler, Updater, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
from common import format_numbers, restricted
from finance_processor import FinanceProcessor
from shared.handlers import CHandler

# Import environemt variables
from env import BALANCE_CHANGE_TEXT, CANCEL_TEXT, ENTER_LOAN_AMOUNT_TEXT, ERROR_TEXT, FINANCE_BOT_TOKEN, FINANCIAL_ACTIVITY_LOG_FILE_PATH, GET_LOGS_TEXT, GREETING_TEXT, HELPER_TEXT, LEND_MONEY_TEXT, LOG_FILE_PATH,\
    PROFITS_TEXT, REQUEST_BALANCE_CHANGE_TEXT, SUCCESS_TEXT, FINANCE_LOGS_CHANNEL_ID, FINANCE_BOT_PARTICIPANTS, LOAN_NOT_IMPLEMENTED_ERROR_TEXT,\
    CHOOSE_LOAN_LENDER_TEXT, WRONG_LOAN_AMMOUNT_TEXT, WRONG_SYNTAX_TEXT, REQUEST_BALANCE_CHANGE_COMMENT_TEXT, logger, action_logger


class FinanceBot:
    @property
    def default_keyboard(self) -> ReplyKeyboardMarkup:
        return ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(BALANCE_CHANGE_TEXT) ,KeyboardButton(LEND_MONEY_TEXT)],
            [KeyboardButton(PROFITS_TEXT), KeyboardButton(GET_LOGS_TEXT)]
        ], 
        resize_keyboard=True, one_time_keyboard=False)
    
    @property
    def dialog_default_keyboard(self) -> ReplyKeyboardMarkup:
        return ReplyKeyboardMarkup([[CANCEL_TEXT]], resize_keyboard=True, one_time_keyboard=False)
    
    @staticmethod
    def log_action(update: Update, context: CallbackContext, action: str):
        """
        Logs an action to both a specified Telegram channel and a local log file.

        This method attempts to send a log message to a specified Telegram channel,
        and always writes the log message to a local log file. If sending the log
        message to the Telegram channel fails, an error is logged.

        Args:
            update (Update): The update event triggering the log action.
            context (CallbackContext): The context of the update event.
            action (str): The action to be logged.

        Returns:
            None
        """
        # Send log message to log channel and saves it to a local file
        try:
            context.bot.send_message(chat_id=FINANCE_LOGS_CHANNEL_ID, text=action, parse_mode='HTML')
        except telegram.error.TelegramError as e:
            logger.error(f'finance_bot.py:log_action(). Exception sending log info to log channel: {e}')
        action_logger.info(action)

    @staticmethod
    def build_loan_keyboard() -> InlineKeyboardMarkup:
        """
        Build an InlineKeyboardMarkup with buttons for each participant.

        The buttons are arranged in a single-column layout, and each button's
        callback data is a string of the format "loan|{participant}".

        Returns:
            InlineKeyboardMarkup: The constructed keyboard.
        """
        keyboard = [[InlineKeyboardButton(participant, callback_data=f'loan|{participant}')] for participant in FINANCE_BOT_PARTICIPANTS]
        return InlineKeyboardMarkup(keyboard)
    
    def __init__(self):
        self.updater = Updater(token=FINANCE_BOT_TOKEN, use_context=True)
        self.dispatcher = self.updater.dispatcher

        # Add start command handler
        start_handler = CommandHandler('start', self.start)
        self.dispatcher.add_handler(start_handler)

        # Add /set_profits and /set_spent command handler (to directly change financial data)
        set_financial_data_handler = CommandHandler(['set_profits', 'set_spent'], self.set_financial_data_handler)
        self.dispatcher.add_handler(set_financial_data_handler)

        # Set help handler
        help_handler = CommandHandler('help', self.help_handler)
        self.dispatcher.add_handler(help_handler)

        # Special handler that terminates any conversation
        cancel_handler = MessageHandler(Filters.text([CANCEL_TEXT]), self.cancel_handler)
        self.dispatcher.add_handler(cancel_handler)

        # Add message handler for the text responses
        text_handler = MessageHandler(Filters.text, self.text_handler)
        self.dispatcher.add_handler(text_handler)

        # Add a loan query handler
        loan_query_handler = CallbackQueryHandler(self.loan_query_handler, pattern=r'^loan\|(.+)$')
        self.dispatcher.add_handler(loan_query_handler)

        self.finance_processor: FinanceProcessor = FinanceProcessor()
        self.c_handler = CHandler()

    def run(self):
        # Start the bot
        self.updater.start_polling()
        self.updater.idle()

    @restricted
    def start(self, update: Update, context: CallbackContext):
        user = update.effective_user
        chat_id = update.effective_chat.id

        # Send message with reply keyboard
        context.bot.send_message(chat_id=chat_id, text=GREETING_TEXT % ('@' + user.username), parse_mode='HTML', reply_markup=self.default_keyboard)

    @restricted
    def help_handler(self, update: Update, context: CallbackContext):
        chat_id = update.effective_chat.id

        # Send message with reply keyboard
        context.bot.send_message(chat_id=chat_id, text=HELPER_TEXT, parse_mode='HTML', reply_markup=self.default_keyboard)

    @restricted
    def text_handler(self, update: Update, context: CallbackContext):
        user = update.effective_user
        chat_id = update.effective_chat.id
        text = update.message.text

        # Handle conversations
        if self.c_handler.has_callback(chat_id):
            return self.c_handler.get_callback(chat_id)(update, context)

        response: str = ''
        keyboard: ReplyMarkup = self.default_keyboard
        if text == PROFITS_TEXT:
            # Generate report about financial data
            response = '<b>Profit:</b>\n\n'
            finance_data = self.finance_processor.get_data()
            for user, user_finances in finance_data.items():
                response += f'💵 <i>{user}</i>: {format_numbers(user_finances["profits"])}$\n'
            response += f'\n💵 <i>Total profit</i>: {format_numbers(sum(finance_data[u]["profits"] for u in finance_data))}$\n\n'
            for user, user_finances in finance_data.items():
                if user_finances['spent'] != 0:
                    response += f'💎 <i>Paid out {user}</i>: {format_numbers(user_finances["spent"])}$\n'
            response = response.rstrip('\n')
        elif text == GET_LOGS_TEXT:
            # Upload log files
            self.send_file(update=update, context=context, filepath=LOG_FILE_PATH)
            return self.send_file(update=update, context=context, filepath=FINANCIAL_ACTIVITY_LOG_FILE_PATH)
        elif text == BALANCE_CHANGE_TEXT:
            self.c_handler.add_callback(chat_id=chat_id, callback=self.balance_change_handler)
            response = REQUEST_BALANCE_CHANGE_TEXT
            keyboard = self.dialog_default_keyboard
        elif text == LEND_MONEY_TEXT:
            if len(FINANCE_BOT_PARTICIPANTS) != 2:
                response = LOAN_NOT_IMPLEMENTED_ERROR_TEXT
            else:
                response = CHOOSE_LOAN_LENDER_TEXT
                keyboard = self.build_loan_keyboard()
        else:
            return
        
        if len(response) > 0:
            context.bot.send_message(chat_id=chat_id, text=response, parse_mode='HTML', reply_markup=keyboard)
    
    @restricted
    def loan_query_handler(self, update: Update, context: CallbackContext):
        """Handle an inline query that has been sent by the user. Issues a loan"""
        chat_id = update.effective_chat.id
        query = update.callback_query
        lender: str = query.data.split('|')[1]

        # Remove the message
        with suppress(Exception):
            context.bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)

        # Make sure loan is given to bot participants
        if not lender in FINANCE_BOT_PARTICIPANTS:
            self.c_handler.remove_callback(chat_id)
            return context.bot.send_message(chat_id=chat_id, text=ERROR_TEXT, parse_mode='HTML', reply_markup=self.default_keyboard)
        elif len(FINANCE_BOT_PARTICIPANTS) != 2:
            self.c_handler.remove_callback(chat_id)
            return context.bot.send_message(chat_id=chat_id, text=LOAN_NOT_IMPLEMENTED_ERROR_TEXT, parse_mode='HTML', reply_markup=self.default_keyboard)

        debtor: str = FINANCE_BOT_PARTICIPANTS[FINANCE_BOT_PARTICIPANTS.index(lender) ^ 1]

        # Ask user for loan amount
        self.c_handler.add_callback(chat_id=chat_id, callback=lambda update, context: self.loan_amount_handler(update, context, lender=lender, debtor=debtor))
        return context.bot.send_message(chat_id, ENTER_LOAN_AMOUNT_TEXT, parse_mode='HTML', reply_markup=self.dialog_default_keyboard)
    
    @restricted
    def set_financial_data_handler(self, update: Update, context: CallbackContext):
        """
        Command handler for the /set_profits and /set_spent commands.
        
        This command requires two arguments: 'user' and 'amount'. It checks if 'user' exists 
        in the FINANCE_BOT_PARTICIPANTS list, and if 'amount' is a positive integer greater than 5. 
        If any condition is not met, it sends a message with the text WRONG_SYNTAX_TEXT.
        Changes corresponding data in financial records for a specified user
        
        Args:
            update (telegram.Update): The current update instance.
            context (telegram.ext.CallbackContext): The context as provided by the library. 
                Contains the state and data from the update.
        
        Returns:
            None
        """
        username: str = update.effective_user.username

        # Check if two arguments are present
        if len(context.args) != 2:
            context.bot.send_message(chat_id=update.effective_chat.id, text=WRONG_SYNTAX_TEXT)
            return

        user, amount = context.args

        # Check if the user exists
        if user not in FINANCE_BOT_PARTICIPANTS:
            context.bot.send_message(chat_id=update.effective_chat.id, text=WRONG_SYNTAX_TEXT)
            return

        # Check if the amount is a positive integer greater than 5
        try:
            amount = int(amount)
            if amount <= 5:
                raise ValueError
        except ValueError:
            return context.bot.send_message(chat_id=update.effective_chat.id, text=WRONG_SYNTAX_TEXT)
        
        # If all checks pass, update financial info
        if update.message.text.startswith('/set_profits'):
            self.finance_processor.set_profits(user=user, amount=amount)
            self.log_action(update, context, f'User @{username} set income of {user} to ${format_numbers(amount)}')
        elif update.message.text.startswith('/set_spent'):
            self.finance_processor.set_spent(user=user, amount=amount)
            self.log_action(update, context, f'User @{username} set expenditures of{user} to ${format_numbers(amount)}')
        else:
            return context.bot.send_message(chat_id=update.effective_chat.id, text=WRONG_SYNTAX_TEXT)
        return self.cancel_handler(update, context)
 
        
    @restricted
    def cancel_handler(self, update: Update, context: CallbackContext):
        """
        Resets current handler whenever uses decides to stop it

        Args:
            update (Update): An object that contains information about the incoming update.
            context (CallbackContext): An object that contains information about the current context of the update.

        Returns:
            None
        """
        chat_id = update.effective_chat.id
        self.c_handler.remove_callback(chat_id)
        context.bot.send_message(chat_id, SUCCESS_TEXT, parse_mode='HTML', reply_markup=self.default_keyboard)

    def loan_amount_handler(self, update: Update, context: CallbackContext, lender: str, debtor: str):
        chat_id = update.effective_chat.id
        text = update.message.text

        # Make sure information is correct
        if not lender in FINANCE_BOT_PARTICIPANTS or not debtor in FINANCE_BOT_PARTICIPANTS:
            self.c_handler.remove_callback(chat_id)
            return context.bot.send_message(chat_id=chat_id, text=ERROR_TEXT, parse_mode='HTML', reply_markup=self.default_keyboard)
        elif len(FINANCE_BOT_PARTICIPANTS) != 2:
            self.c_handler.remove_callback(chat_id)
            return context.bot.send_message(chat_id=chat_id, text=LOAN_NOT_IMPLEMENTED_ERROR_TEXT, parse_mode='HTML', reply_markup=self.default_keyboard)

        # Make sure entered amount is correct
        if not text.isdigit() or int(text) < 5:
            self.c_handler.add_callback(chat_id=chat_id, callback=lambda update, context: self.loan_amount_handler(update, context, lender=lender, debtor=debtor))
            return context.bot.send_message(chat_id, WRONG_LOAN_AMMOUNT_TEXT, parse_mode='HTML', reply_markup=self.dialog_default_keyboard)

        loan_amount: int = int(text)
        self.log_action(update=update, context=context, action=f'User {lender} lended ${format_numbers(loan_amount)} to {debtor}')
        self.finance_processor.process_loan(lender=lender, debtor=debtor, amount=loan_amount)
        return self.cancel_handler(update=update, context=context)

    def balance_change_handler(self, update: Update, context: CallbackContext):
        """
        Handles the initial phase of a user-requested change in total balance.
        The function first validates if the entered amount for balance change 
        is a valid integer. If the input is invalid, it sends an error message back 
        to the user and requests for a new input. If the input is valid, the function
        sets a callback to the comment handler function for the next user input.

        Args:
            update (Update): The update event triggering the balance change.
            context (CallbackContext): The context of the update event.

        Returns:
            None
        """
        user = update.effective_user
        chat_id = update.effective_chat.id
        text = update.message.text

        if not re.match(r'^-?\d+$', text):
            self.c_handler.add_callback(chat_id=chat_id, callback=self.balance_change_handler)
            return context.bot.send_message(chat_id, ERROR_TEXT, parse_mode='HTML', reply_markup=self.dialog_default_keyboard)

        balance_change = int(text)
        self.c_handler.add_callback(chat_id=chat_id, callback=lambda update, context: self.balance_change_comment_handler(update, context, balance_change=balance_change))
        return context.bot.send_message(chat_id, REQUEST_BALANCE_CHANGE_COMMENT_TEXT, parse_mode='HTML', reply_markup=self.dialog_default_keyboard)


    def balance_change_comment_handler(self, update: Update, context: CallbackContext, balance_change: int):
        """
        Handles the second phase of a user-requested change in total balance. 
        It retrieves the comment input from the user, processes the balance change,
        logs the action with the comment, and sends the log info to the telegram channel.

        Args:
            update (Update): The update event triggering the balance change.
            context (CallbackContext): The context of the update event.
            balance_change (int): The balance change amount provided by the user.

        Returns:
            None
        """
        user = update.effective_user
        chat_id = update.effective_chat.id
        comment: str = update.message.text
        self.log_action(update=update, context=context, action=f'User @{user.username} {"decreased" if balance_change < 0 else "increased"} total account balance by ${format_numbers(balance_change)}$\nExplanation: {comment}')
        self.finance_processor.process_balance_change(balance=balance_change)
        return self.cancel_handler(update=update, context=context)

    def send_file(self, update: Update, context: CallbackContext, filepath: str):
        """
        This function uploads a file to a user on Telegram.

        Args:
            update (Update): An object that contains information about the incoming update.
            context (CallbackContext): An object that contains information about the current context of the update.
            filepath (str): The path to the file to be sent.

        Returns:
            None
        """
        chat_id = update.effective_chat.id

        # Exceptions correspond to files being empty
        with suppress(Exception), open(filepath, 'rb') as file:
            context.bot.send_document(chat_id=chat_id, document=file)
