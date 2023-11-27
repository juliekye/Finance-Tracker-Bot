import os
from typing import List


# Reads all environment variables
try:
    ENV_VARS = ['BASE_DIR', 'DEVELOPEMENT_ENVIRONMENT', 'TWO_FA_BOT_TOKEN_DEV', 'TWO_FA_BOT_LINK_DEV', 'TWO_FA_BOT_TOKEN_PRODUCTION', 
                    'TWO_FA_BOT_LINK_PRODUCTION', 'PGP_PASSPHRASE', 'USERNAME', 'PGP_PASSPHRASE', 'ALLOWED_USERS_FINANCE_BOT', 'FINANCE_BOT_TOKEN_DEV',
                    'FINANCE_BOT_LINK_DEV', 'FINANCE_BOT_TOKEN_PRODUCTION', 'FINANCE_BOT_LINK_PRODUCTION', 'FINANCE_BOT_PARTICIPANTS',
                    'FINANCE_LOGS_CHANNEL_ID']

    missing_vars = [var for var in ENV_VARS if os.environ.get(var) is None]
    if missing_vars:
        raise Exception(f'Missing environment variables: {", ".join(missing_vars)}')

    BASE_DIR: str = os.environ.get('BASE_DIR')
    DEVELOPEMENT_ENVIRONMENT: bool = os.environ.get('DEVELOPEMENT_ENVIRONMENT') == 'true'
    PGP_PASSPHRASE: str = os.environ.get('PGP_PASSPHRASE')
    USERNAME: str = os.environ.get('USERNAME')
    PGP_PASSPHRASE: str = os.environ.get('PGP_PASSPHRASE')
    ALLOWED_USERS_FINANCE_BOT: List[str] = os.environ.get('ALLOWED_USERS_FINANCE_BOT').split(',')
    FINANCE_BOT_PARTICIPANTS: List[str] = os.environ.get('FINANCE_BOT_PARTICIPANTS').split(',')
    FINANCE_LOGS_CHANNEL_ID: int = int(os.environ.get('FINANCE_LOGS_CHANNEL_ID'))

    if DEVELOPEMENT_ENVIRONMENT:
        # 2FA bot
        TWO_FA_BOT_TOKEN: str = os.environ.get('TWO_FA_BOT_TOKEN_DEV')
        TWO_FA_BOT_LINK: str = os.environ.get('TWO_FA_BOT_LINK_DEV')

        # Finance bot
        FINANCE_BOT_TOKEN: str = os.environ.get('FINANCE_BOT_TOKEN_DEV')
        FINANCE_BOT_LINK: str = os.environ.get('FINANCE_BOT_LINK_DEV')

    else:
        # 2FA bot
        TWO_FA_BOT_TOKEN: str = os.environ.get('TWO_FA_BOT_TOKEN_PRODUCTION')
        TWO_FA_BOT_LINK: str = os.environ.get('TWO_FA_BOT_LINK_PRODUCTION')

        # Finance bot
        FINANCE_BOT_TOKEN: str = os.environ.get('FINANCE_BOT_TOKEN_PRODUCTION')
        FINANCE_BOT_LINK: str = os.environ.get('FINANCE_BOT_LINK_PRODUCTION')


except:
    raise Exception('Error defining environment variables!')
