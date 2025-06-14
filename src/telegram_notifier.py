import os
from telegram import Bot
from telegram.error import TelegramError
from .logger import setup_logger
from .config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

logger = setup_logger(__name__)

class TelegramNotifier:
    def __init__(self):
        self.bot = Bot(token=TELEGRAM_BOT_TOKEN)
        self.chat_id = TELEGRAM_CHAT_ID
        self.bot.delete_webhook()
        self.bot.set_webhook(url=None)

    async def send_notification(self, message):
        """
        send a message to the Telegram chat
        
        Args:
            message (str): message to send
        """
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML',
                disable_notification=False
            )
            logger.info("Notification sent successfully to Telegram chat.")
        except TelegramError as e:
            logger.error(f"Error when send a notification: {str(e)}")

    async def notify_available_slots(self, available_slots):
        """
        Notify about available slots
        Args:
            available_slots (list): List of available slots
        """
        if not available_slots:
            return

        message = "🎾 <b>¡Turnos disponibles encontrados!</b>\n\n"
        
        for slot in available_slots:
            message += f"📅 <b>Fecha:</b> {slot['fecha']}\n"
            message += f"⏰ <b>Hora:</b> {slot['hora']}\n"
            message += f"🏸 <b>Cancha:</b> {slot['cancha']}\n"
            message += f"ℹ️ <b>Características:</b> {slot['caracteristicas']}\n"
            message += "➖➖➖➖➖➖➖➖➖➖\n"

        await self.send_notification(message) 