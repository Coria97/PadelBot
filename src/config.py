"""
Configuración del proyecto
"""
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de la URL (se actualizará cuando se proporcione la página)
BASE_URL = os.getenv('BASE_URL', '')

# Configuración de intervalos de monitoreo (en minutos)
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', '5'))

# Configuración de notificaciones
ENABLE_NOTIFICATIONS = os.getenv('ENABLE_NOTIFICATIONS', 'True').lower() == 'true'

# Configuración de Telegram
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '') 