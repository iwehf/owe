import logging
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes
from owe.owe_agent.owe_agent import OweAgent
from PIL import Image
import io
from pathlib import Path
import asyncio

logger = logging.getLogger(__name__)

class TGBot:
    def __init__(self, agent: OweAgent, bot_token: str) -> None:

        # Owe Agent
        logger.info("Initializing Owe Agent...")
        self.oweAgent = agent

        # TG Application
        logger.info("Initializing TG Bot...")
        self.application = ApplicationBuilder().token(bot_token).build()
        resp_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), self.respond)
        self.application.add_handler(resp_handler)
        self.application.add_error_handler(self.error_handler)

    def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        logger.error("Exception while handling an update:", exc_info=context.error)

    def read_image_file(self, image_path: Path) -> bytes:
        image = Image.open(image_path)
        image_bytes = io.BytesIO()
        image.save(image_bytes, format="JPEG")
        return image_bytes.getvalue()

    async def respond(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_input = update.message.text

        logger.debug(f"message from user id: {context._user_id}")
        resp = await self.oweAgent.get_response(user_input, f"{context._user_id}")

        if resp["image"] is not None:
            image_bytes = await asyncio.to_thread(self.read_image_file, resp["image"])
            await context.bot.send_photo(chat_id=update.effective_chat.id, photo=image_bytes)
        elif resp["text"] is not None:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=resp["text"])

    def start(self) -> None:
        logger.info("Starting TG Bot...")
        self.application.run_polling()
