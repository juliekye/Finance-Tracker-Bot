from functools import wraps
from telegram import Update
from telegram.ext import CallbackContext
from env import ALLOWED_USERS_FINANCE_BOT, logger


def format_numbers(number: int) -> str:
    """
    Formats a number by splitting it into tuples of three digits and placing spaces between them.
    
    Args:
        number (int): The number to be formatted.
        
    Returns:
        str: The formatted number.
    """
    number = int(number)
    if number == 0:
        return str(number)

    # Convert the number to a string and remove any leading '+' or '-'
    number_str = str(number).lstrip('+-')

    # Split the number into groups of three digits from the right
    groups = []
    while number_str:
        groups.append(number_str[-3:])
        number_str = number_str[:-3]

    # Reverse the groups and join them with spaces
    formatted_number = ' '.join(groups[::-1])

    # Add the leading '+' or '-' sign if applicable
    if number < 0:
        formatted_number = '-' + formatted_number

    return formatted_number


def restricted(func):
    """
    A decorator to restrict access to certain bot functions based on username.

    This decorator wraps a bot function so that it only processes updates from 
    users whose usernames are in the ALLOWED_USERS_FINANCE_BOT list. If the user 
    is not in the list, a warning is logged and the function returns None. If the 
    user is in the list, the original function is called as normal.

    Args:
        func (Callable): The bot function to be wrapped.

    Returns:
        Callable: The wrapped function, which will only process updates from 
                  allowed users.

    """
    @wraps(func)
    def wrapped(self, update: Update, context: CallbackContext, *args, **kwargs):
        user = update.effective_user
        chat_id = update.effective_chat.id
        if user.username not in ALLOWED_USERS_FINANCE_BOT:
            logger.warning(f'Unauthorized access denied from User: username=@{user.username}, id={chat_id}')
            return
        return func(self, update, context, *args, **kwargs)
    return wrapped
