import logging
import os
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes
from owe.owe_agent.owe_agent import OweAgent
import base64

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

class TGBot:
    def __init__(self) -> None:

        # Owe Agent
        logging.info("Initializing Owe Agent...")
        self.oweAgent = OweAgent()

        # TG Application
        logging.info("Initializing TG Bot...")
        self.application = ApplicationBuilder().token(os.getenv("TG_BOT_TOKEN")).build()
        resp_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), self.respond)
        self.application.add_handler(resp_handler)

    async def respond(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_input = update.message.text
        resp = self.oweAgent.get_response(user_input)

        if resp["image"] is not None:

            img_bytes = resp["image"].encode("utf-8")
            img_data = base64.b64decode(img_bytes)

            await context.bot.send_photo(chat_id=update.effective_chat.id, photo=img_data)
        elif resp["text"] is not None:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=resp["text"])

    def start(self) -> None:
        logging.info("Starting TG Bot...")
        self.application.run_polling()
