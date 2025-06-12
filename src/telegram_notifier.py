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
        Envía una notificación a través de Telegram
        
        Args:
            message (str): Mensaje a enviar
        """
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML',
                disable_notification=False
            )
            logger.info("Notificación enviada exitosamente a Telegram")
        except TelegramError as e:
            logger.error(f"Error al enviar notificación a Telegram: {str(e)}")

    async def notify_available_slots(self, available_slots):
        """
        Notifica sobre los turnos disponibles después de las 17:00 horas
        
        Args:
            available_slots (list): Lista de turnos disponibles
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