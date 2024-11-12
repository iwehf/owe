from dotenv import load_dotenv
from owe.telegram.bot import TGBot

load_dotenv()

bot = TGBot()
bot.start()
