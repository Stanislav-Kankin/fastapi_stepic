import requests
import logging

TELEGRAM_BOT_TOKEN = '6976322402:AAGdI4BnTfuHJCkKiO87CG03zsn-gAkRBeU'
TELEGRAM_CHAT_ID = -1002371910425

logger = logging.getLogger(__name__)


def format_number(value):
    return "{:,.2f}".format(value).replace(",", " ").replace(".00", "")


def send_telegram_message(message, user_data):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        logger.info("Message sent to Telegram successfully")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending message to Telegram: {e}")
        logger.error(f"Response content: {response.content}")
