import os
from dotenv import load_dotenv

# load environment variables from .env file
load_dotenv()

# Configuration of the URL (will be updated when the page is provided)
BASE_URL = os.getenv('BASE_URL', '')

# Configuration of monitoring intervals (in minutes)
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', '5'))

# Configuration of notifications
ENABLE_NOTIFICATIONS = os.getenv('ENABLE_NOTIFICATIONS', 'True').lower() == 'true'

# Configuration of Telegram
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '') 