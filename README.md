# PadelBot - Padel Court Monitor

An intelligent bot that automatically monitors the availability of padel court slots on specific websites and notifies users through Telegram when slots become available.

## 🎯 Features

- **Automatic monitoring**: Periodically checks court availability
- **Real-time notifications**: Sends alerts through Telegram
- **Bot interface**: Interactive commands to manage monitoring
- **Scalability**: Architecture with Celery and Redis for distributed processing
- **Data persistence**: Information storage in SQLite database
- **Complete logging**: Logging system for debugging and monitoring

## 🚀 Installation

### Prerequisites

- Docker

### Installation

1. **Clone and configure**
   ```bash
   git clone <repository-url>
   cd PadelBot
   cp .env.example .env
   # Edit .env with your configurations
   ```

2. **Run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

## ⚙️ Configuration

### Environment Variables

Copy the `.env.example` file to `.env` and configure the following variables:

```env
# URL of the page to monitor
BASE_URL=url

# Check interval in minutes
CHECK_INTERVAL=2

# Enable notifications
ENABLE_NOTIFICATIONS=True

# Telegram Configuration
TELEGRAM_BOT_TOKEN=your_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# Celery configuration
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
```

### Telegram Configuration

1. **Create a bot**: Talk to [@BotFather](https://t.me/botfather) on Telegram
2. **Get the token**: Save the provided token in `TELEGRAM_BOT_TOKEN`
3. **Get Chat ID**: Use [@userinfobot](https://t.me/userinfobot) to get your Chat ID

### Bot Commands

Once the bot is running, you can interact with it on Telegram:

- `/start` - Start the bot and show available commands
- `/status` - View current monitoring status
- `/check` - Manually check availability
- `/subscribe` - Automatically check availability
- `/help` - Show help

## 📁 Project Structure

```
PadelBot/
├── src/
│   ├── main.py              # Main entry point
│   ├── telegram_bot.py      # Telegram bot
│   ├── scraper.py           # Web scraping and monitoring
│   ├── config.py            # Configuration
│   ├── logger.py            # Logging system
│   ├── tasks/               # Celery tasks
│   └── database/            # Models and database management
├── data/                    # Persistent data
├── logs/                    # Log files
├── requirements.txt         # Python dependencies
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Service orchestration
├── .env.example            # Environment variables template
└── README.md               # This file
```

## 🔧 Main Dependencies

- **requests**: HTTP client for making web requests
- **beautifulsoup4**: HTML parsing
- **selenium**: Web browser automation
- **python-telegram-bot**: Telegram API
- **celery**: Asynchronous task processing
- **redis**: Message broker
- **SQLAlchemy**: Database ORM
- **schedule**: Task scheduling
