import logging
import os
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes
from owe.owe_agent.owe_agent import OweAgent
from PIL import Image
import io

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

class TGBot:
    def __init__(self, agent_preset_prompt: str) -> None:

        # Owe Agent
        logging.info("Initializing Owe Agent...")
        self.oweAgent = OweAgent(agent_preset_prompt)

        # TG Application
        logging.info("Initializing TG Bot...")
        self.application = ApplicationBuilder().token(os.getenv("TG_BOT_TOKEN")).build()
        resp_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), self.respond)
        self.application.add_handler(resp_handler)

    async def respond(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_input = update.message.text

        logging.debug(f"message from user id: {context._user_id}")
        resp = self.oweAgent.get_response(user_input, f"{context._user_id}")

        if resp["image"] is not None:

            image = Image.open(resp["image"])
            image_bytes = io.BytesIO()
            image.save(image_bytes, format="JPEG")

            await context.bot.send_photo(chat_id=update.effective_chat.id, photo=image_bytes.getvalue())
        elif resp["text"] is not None:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=resp["text"])

    def start(self) -> None:
        logging.info("Starting TG Bot...")
        self.application.run_polling()
