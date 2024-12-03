import logging
from logging.handlers import RotatingFileHandler

import requests

from config.config import Config, load_config


config: Config = load_config()

TOKEN = config.tgbot.token
ADMIN_IDS = config.tgbot.admin_ids
URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"


def send_critical_to_bot(message: str):
    for admin_id in ADMIN_IDS:
        payload = {"chat_id": admin_id, "text": f"[CRITICAL ERROR]: {message}"}
        try:
            requests.post(URL, json=payload)
        except Exception as e:
            logger.warning(f"Failed to send message to Telegram: {e}")


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    "%(filename)s:%(lineno)d #%(levelname)-8s "
    "[%(asctime)s] - %(name)s - %(message)s",
)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)

warning_handler = RotatingFileHandler(
    "../logs/warnings.log", maxBytes=1000000, backupCount=5,
)
warning_handler.setLevel(logging.WARNING)
warning_handler.setFormatter(formatter)


class WarningFilter(logging.Filter):
    def only_warning_logs_filter(self, record):
        return (
            record.levelno < logging.ERROR
        )  # Только WARNING, не ERROR и не CRITICAL


warning_handler.addFilter(WarningFilter())

error_handler = RotatingFileHandler(
    "../logs/errors.log", maxBytes=1000000, backupCount=5,
)
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(formatter)


class TelegramHandler(logging.Handler):
    def emit(self, record):
        log_entry = self.format(record)
        send_critical_to_bot(log_entry)


telegram_handler = TelegramHandler()
telegram_handler.setLevel(logging.CRITICAL)
telegram_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(warning_handler)
logger.addHandler(error_handler)
logger.addHandler(telegram_handler)

if __name__ == "__main__":
    logger.debug("This is a DEBUG message")  # Пойдет в консоль
    logger.info("This is an INFO message")  # Пойдет в консоль
    logger.warning("This is a WARNING message")  # Запишется в warnings.log
    logger.error("This is an ERROR message")  # Запишется в errors.log
    logger.critical(
        "This is a CRITICAL message",
    )  # Запишется в errors.log и отправится в Telegram
