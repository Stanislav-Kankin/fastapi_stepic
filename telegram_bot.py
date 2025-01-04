import requests
import logging

TELEGRAM_BOT_TOKEN = '8136129004:AAGt6Ji-Lis8Hh5UwKDKWwQaSqEl_FYk43Y'
TELEGRAM_CHAT_ID = -4703714170

logger = logging.getLogger(__name__)


def format_number(value):
    return "{:,.0f}".format(value).replace(",", " ")


def send_telegram_message(message, user_data):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'Markdown'  # Включаем поддержку Markdown
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        logger.info("Message sent to Telegram successfully")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending message to Telegram: {e}")
        logger.error(f"Response content: {response.content}")
