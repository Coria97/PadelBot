from datetime import datetime

from typing import Set

from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.error import TelegramError

from src.logger import setup_logger
from src.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from src.database.operations import available_slots_manager, subscription_manager

logger = setup_logger(__name__)

class TelegramBot:
    def __init__(self):
        # Initialize the bot
        self.bot = Bot(token=TELEGRAM_BOT_TOKEN)
        self.chat_ids: Set[int] = {TELEGRAM_CHAT_ID}
        self.application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        
        # Register the commands
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("check", self.check_command))
        self.application.add_handler(CommandHandler("subscribe", self.subscribe_command))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Manage the /start command"""
        chat_id = update.effective_chat.id
        self.chat_ids.add(chat_id)
        await update.message.reply_text(
            "¡Hola! Soy PadelBot 🤖\n"
            "Te ayudaré a monitorear los turnos disponibles.\n"
            "Usa /help para ver los comandos disponibles."
        )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Manage the /help command"""
        help_text = (
            "📋 <b>Comandos disponibles:</b>\n\n"
            "/start - Iniciar el bot\n"
            "/help - Mostrar esta ayuda\n"
            "/status - Ver el estado actual del monitoreo\n"
            "/check DD/MM HH:MM - Verificar disponibilidad para una fecha y hora específica\n"
            "Ejemplo: /check 25/03 18:00"
        )
        await update.message.reply_text(help_text, parse_mode='HTML')

    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Manage the /status command"""
        await update.message.reply_text(
            "🔄 El bot está activo y monitoreando turnos.\n"
            "Te notificaré cuando encuentre turnos disponibles."
        )

    async def check_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Manage the /check command"""
        try:
            # Verify if the arguments are provided
            if not context.args or len(context.args) != 2:
                await update.message.reply_text(
                    "❌ Formato incorrecto. Por favor usa:\n"
                    "/check DD/MM HH:MM\n"
                    "Ejemplo: /check 25/03 18:00"
                )
                return

            # Get the date and time
            date_str, time_str = context.args
            
            # Add current year to the date
            current_year = datetime.now().year
            date_with_year = f"{date_str}/{current_year}"
            
            # Get the available slots
            available_slots = available_slots_manager.get_available_slots_by_day_and_hour(date_with_year, time_str)

            # Notify the user
            if available_slots:
                message = self.create_message(available_slots)
            else:
                message = "❌ No hay turnos disponibles para esa fecha y hora."
            
            await update.message.reply_text(message, parse_mode='HTML')

        except Exception as e:
            logger.error(f"Error en el comando check: {str(e)}")
            await update.message.reply_text(
                "❌ Ocurrió un error al verificar la disponibilidad.\n"
                "Por favor, intenta nuevamente más tarde."
            )

    async def subscribe_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Manage the /subscribe command"""
        chat_id = update.effective_chat.id
        self.chat_ids.add(chat_id)

        if not context.args or len(context.args) != 2:
            await update.message.reply_text(
                "❌ Formato incorrecto. Por favor usa:\n"
                "/subscribe DD/MM HH:MM\n"
                "Ejemplo: /subscribe 25/03 18:00"
            )
            return
        
        # Get the date and time
        date_str, time_str = context.args
        date = datetime.strptime(date_str, "%d/%m")
        time = datetime.strptime(time_str, "%H:%M")

        # Subscribe to the available slots
        subscription_manager.add_subscription(date, time, chat_id)
        await update.message.reply_text("Te has suscrito al monitoreo de turnos.")


    async def send_notification(self, message, chat_id):
        """
        Send a message to a specific Telegram chat
        
        Args:
            message (str): message to send
            chat_id (int): target chat ID
        """
        try:
            await self.bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode='HTML',
                disable_notification=False
            )
            logger.info(f"Notification successfully sent to chat {chat_id}")
        except TelegramError as e:
            logger.error(f"Error sending notification to chat {chat_id}: {str(e)}")

    async def notify_available_slots(self, available_slots, chat_id):
        """
        Notify about available slots
        Args:
            available_slots (list): List of available slots
        """
        if not available_slots:
            return
        message = self.create_message(available_slots)
        await self.send_notification(message, chat_id)

    def create_message(self, available_slots):
        message = "🎾 <b>¡Turnos disponibles encontrados!</b>\n\n"
        for slot in available_slots:
            message += f"📅 <b>Fecha:</b> {slot['fecha']}\n"
            message += f"⏰ <b>Hora:</b> {slot['hora']}\n"
            message += f"🏸 <b>Cancha:</b> {slot['cancha']}\n"
            message += "➖➖➖➖➖➖➖➖➖➖\n"
        return message