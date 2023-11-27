import json
import os
from typing import Dict
from filelock import FileLock

# Import env variables
from env import FINANCE_INFO_FILE, FINANCE_BOT_PARTICIPANTS, logger


class FinanceProcessor:
    """
    Processor for handling and persisting financial information of bot users.
    
    The financial information is stored in a JSON file specified by the
    FINANCE_INFO_FILE constant. If the file does not exist upon instantiation,
    it is created with initial data.
    
    A file lock is used when reading or writing to the file to ensure thread safety.
    """
    _data: Dict[str, Dict[str, int]]

    def __init__(self):
        """
        Initialize the FinanceProcessor, creating the financial data file if necessary.
        """
        self.lock = FileLock(FINANCE_INFO_FILE + '.lock')
        if not os.path.exists(FINANCE_INFO_FILE):
            initial_data = {participant: {'profits': 0.0, 'spent': 0.0} for participant in FINANCE_BOT_PARTICIPANTS}
            with self.lock:
                with open(FINANCE_INFO_FILE, 'w') as f:
                    json.dump(initial_data, f)
        self._refresh_data()

    def _refresh_data(self):
        """
        Load the financial data from the file into the _data attribute.

        The file is locked during the operation to prevent concurrent modifications.
        """
        with self.lock:
            with open(FINANCE_INFO_FILE, 'r') as f:
                self._data = json.load(f)

    def _update_data(self):
        """
        Save the current financial data from the _data attribute to the file.

        The file is locked during the operation to prevent concurrent modifications.
        """
        with self.lock:
            with open(FINANCE_INFO_FILE, 'w') as f:
                json.dump(self._data, f)

    def get_data(self) -> Dict[str, Dict[str, int]]:
        """
        Refresh and return the financial data of the bot users.

        The data returned is a nested dictionary where the outer dictionary's keys
        are usernames and the values are inner dictionaries with keys 'profits' and 'spent'.

        Returns:
            Dict[str, Dict[str, int]]: The financial data of the bot users.
        """
        self._refresh_data()
        return self._data

    def process_balance_change(self, balance: int):
        """
        Process a change in total balance, dividing the change evenly among all users.

        The change is rounded to the nearest integer and added to each user's profits.

        Args:
            balance (int): The total change in balance to be processed.
        """
        self._refresh_data()
        n_users = len(self._data)
        change = round(balance / n_users)
        for user in self._data:
            self._data[user]['profits'] += change
        self._update_data()

    def process_loan(self, lender: str, debtor: str, amount: int):
        """
        Process a loan between two users, updating their profits accordingly.

        If either of the users do not exist, a warning is logged and no changes are made.

        Args:
            lender (str): The username of the user giving the loan.
            debtor (str): The username of the user receiving the loan.
            amount (int): The amount of the loan.
        """
        # Increase lender's money as they performed a real world transaction and thus require to have it compensated on the account
        self._refresh_data()
        if lender in self._data and debtor in self._data:
            self._data[lender]['profits'] += amount
            self._data[debtor]['profits'] -= amount
            self._update_data()
        else:
            logger.warning(f"finance_processor.py:process_loan(). Loan operation failed: Check if users '{lender}' and '{debtor}' exist.")

    def set_profits(self, user: str, amount: int):
        """
        Sets the profits of a given user to a specified amount.

        Args:
            user (str): The name of the user whose profits are to be set.
            amount (int): The amount to which the profits are to be set. It should be greater than 1000.

        Returns:
            None, but logs a warning if the user doesn't exist or if the amount is less than or equal to 1000.
        """
        self._refresh_data()
        if not user in self._data:
            return logger.warning(f"finance_processor.py:set_profits(). Failed to set profits: Check if user '{user}' exists.")
        if amount < 1000:
            return logger.warning(f"finance_processor.py:set_profits(). Failed to set profits: amount should be > 1000. Supplied amount: {amount}")
        
        self._data[user]['profits'] = amount
        self._update_data()

    def set_spent(self, user: str, amount: int):
        """
        Sets the spent value of a given user to a specified amount.

        Args:
            user (str): The name of the user whose spent value is to be set.
            amount (int): The amount to which the spent value is to be set.

        Returns:
            None, but logs a warning if the user doesn't exist.
        """
        self._refresh_data()
        if not user in self._data:
            return logger.warning(f"finance_processor.py:set_spent(). Failed to set spent: Check if user '{user}' exists.")
        
        self._data[user]['spent'] = amount
        self._update_data()
