import logging
import os
import sys
import time
from http import HTTPStatus

import requests
from dotenv import load_dotenv
from telegram import Bot

from exceptions import (EmptyListException, InvalidApiExc, InvalidResponseExc,
                        InvalidTokenException, InvalidJsonExc)

load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter(
    '%(asctime)s [%(levelname)s] - %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)

PRACTICUM_TOKEN = os.getenv('PR_TOKEN')
TELEGRAM_TOKEN = os.getenv('MY_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot, message):
    """Отправка сообщения."""
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        logger.info(f'Бот отправил сообщение: {message}')
    except Exception as error:
        logger.error(f'Ошибка отправки сообщения: {error}')


def get_api_answer(current_timestamp):
    """Проверка успешности запроса к API и возврат ответа API."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        homework_statuses = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params=params
        )
    except Exception as error:
        raise InvalidApiExc(f'Ошибка ответа API: {error}')
    status = homework_statuses.status_code
    if status != HTTPStatus.OK:
        logger.error(f'Ответ API: {status}')
        raise InvalidResponseExc(f'Status_code: {status}')
    try:
        return homework_statuses.json()
    except Exception as error:
        raise InvalidJsonExc(f'Ошибка декодирования JSON: {error}')


def check_response(response):
    """Проверка ответа API и возврат списка работ."""
    if not isinstance(response, dict):
        raise TypeError('not dict после .json() в ответе API')
    if 'homeworks' and 'current_date' not in response:
        raise InvalidApiExc('Некорректный ответ API')
    if not isinstance(response.get('homeworks'), list):
        raise TypeError('not list в ответе API по ключу homeworks')
    if not response.get('homeworks'):
        raise EmptyListException('Новых статусов нет')
    try:
        return response.get('homeworks')[0]
    except Exception as error:
        raise InvalidResponseExc(f'Из ответа не получен список работ: {error}')


def parse_status(homework):
    """Получение статуса домашней работы из ответа API."""
    if not homework:
        raise InvalidApiExc('Словарь homeworks пуст')
    if 'homework_name' not in homework:
        raise KeyError('Ключ homework_name отсутствует')
    if 'status' not in homework:
        raise KeyError('Ключ status отсутствует')
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if homework_status not in VERDICTS:
        raise KeyError(f'{homework_status} отсутствует в словаре verdicts')
    verdict = VERDICTS[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверка наличия всех токенов в переменных окружения."""
    tokens = [PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]
    return all(tokens)


def main():
    """Основная логика работы бота."""
    bot = Bot(token=TELEGRAM_TOKEN)
    current_timestamp = 0
    last_error = ''
    last_message = ''
    if not check_tokens():
        logger.critical('Недоступны переменные окружения!')
        raise InvalidTokenException('Недоступны переменные окружения')
    while True:
        try:
            logger.debug('Начало итерации, запрос к API')
            response = get_api_answer(current_timestamp)
            current_timestamp = response.get('current_date')
            homeworks = check_response(response)
            status = parse_status(homeworks)
            if status != last_message:
                send_message(bot, status)
                last_message = status
        except EmptyListException:
            logger.debug('Новых статусов в ответе API нет')
        except (InvalidApiExc, TypeError, KeyError, Exception) as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(message)
            if error != last_error:
                send_message(bot, message)
                last_error = error
        else:
            logger.debug('Успешная итерация - нет исключений')
        finally:
            logger.debug('Итерация завершена')
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
