# Import environment variables
from TWOFA_bot import TwoFABot
from env import *


if __name__ == '__main__':
    bot = TwoFABot(TWO_FA_BOT_TOKEN)
    bot.run()
