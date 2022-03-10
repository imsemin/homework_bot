import copy
import logging
import os
import sys
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

import exceptions as ex

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)


load_dotenv()


PRACTICUM_TOKEN = os.getenv("TOKEN_PRAKT")
TELEGRAM_TOKEN = os.getenv("TOKEN_TEL")
TELEGRAM_CHAT_ID = os.getenv("CHAT_ID")


RETRY_TIME = 600
ENDPOINT = "https://practicum.yandex.ru/api/user_api/homework_statuses/"
HEADERS = {"Authorization": f"OAuth {PRACTICUM_TOKEN}"}


HOMEWORK_STATUSES = {
    "approved": "Работа проверена: ревьюеру всё понравилось. Ура!",
    "reviewing": "Работа взята на проверку ревьюером.",
    "rejected": "Работа проверена: у ревьюера есть замечания.",
}


def send_message(bot, message):
    """Отправка сообщений."""
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        logger.info("Сообщение отправлено")
    except Exception as error:
        logger.error(f"Сообщение не отправлено по причине: {error}")


def get_api_answer(current_timestamp):
    """API запрос к ресурсу."""
    timestamp = current_timestamp or int(time.time())
    params = {"from_date": timestamp}
    response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    if response.status_code == HTTPStatus.OK:
        return response.json()
    elif response.status_code != HTTPStatus.OK:
        logger.error(f"Ошибка статуса: {response.status_code}")
        raise requests.exceptions.HTTPError(
            f"Ошибка статуса: {response.status_code}"
        )
    else:
        raise requests.exceptions.InvalidURL(f"Проблема с запросом к URL")


def check_response(response):
    """Проверка ответа API."""
    if type(response) != dict:
        raise TypeError("Ответ API не соответствует типу данных Python")
    elif type(response["homeworks"]) != list:
        raise TypeError("Ответ API не является списком")
    elif len(response["homeworks"]) == 0:
        logger.info("Отсутствует актуальное домашнее задание")
    else:
        return response["homeworks"]


def parse_status(homework):
    """Получаем наименование и статус домашней работы.
    Формируем текст с полученными данными для отправки."""
    if "homework_name" not in homework:
        logger.error("API ответ не содержит ключ homework_name.")
        raise KeyError("API ответ не содержит ключ homework_name.")
    homework_name = homework["homework_name"]
    if "status" not in homework:
        logger.error("API ответ не содержит ключ status.")
        raise KeyError("API ответ не содержит ключ status.")
    homework_status = homework["status"]
    verdict = HOMEWORK_STATUSES[homework_status]
    if homework_status not in HOMEWORK_STATUSES:
        logger.error("Статус неопределен.")
        raise KeyError("Статус неопределен.")

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    "Проверка доступности переменных окружения."
    if PRACTICUM_TOKEN and TELEGRAM_TOKEN and TELEGRAM_CHAT_ID is not None:
        return True
    else:
        logger.critical(
            "Отсутствие обязательных переменных окружения. Программа принудительно остановлена."
        )


def main():

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    main_error = ""

    if not check_tokens():
        raise ex.TokenError("Отсутствие обязательных переменных окружения.")

    while True:
        try:
            response = get_api_answer(current_timestamp)
            homeworks = check_response(response)
            if homeworks:
                message = parse_status(homeworks[0])
                send_message(bot, message)
            current_timestamp = int(time.time())
            time.sleep(RETRY_TIME)
        except Exception as error:
            message = f"Сбой в работе программы: {error}"
            logger.error(message)
            if str(error) != str(main_error):
                send_message(bot, message)
            else:
                logger.info(f"Ошибка {error} не исправлена")
            main_error = copy.deepcopy(error)
            time.sleep(RETRY_TIME)


if __name__ == "__main__":
    main()
