import os
from dotenv import load_dotenv
import requests
import time
from telegram import Bot
from exceptions import (InvalidTokenException,
                        InvalidApiExc,
                        EmptyListException)

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PR_TOKEN')
TELEGRAM_TOKEN = os.getenv('MY_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('CHAT_ID')

RETRY_TIME = 10
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot, message):
    """Отправка сообщения."""
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)


def get_api_answer(current_timestamp):
    """Проверка успешности запроса к API и возврат ответа API."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    homework_statuses = requests.get(
        ENDPOINT,
        headers=HEADERS,
        params=params
    )
    if homework_statuses.status_code != 200:
        homework_statuses.raise_for_status()
    return homework_statuses.json()


def check_response(response):
    """Проверка ответа API и возврат списка работ."""
    if type(response) is not dict:
        raise TypeError('not dict после .json() в ответе API')
    if len(response) != 2:
        raise InvalidApiExc('Некорректный ответ API')
    elif type(response.get('homeworks')) is not list:
        raise InvalidApiExc('not list в ответе API по ключу homeworks')
    elif not response.get('homeworks'):
        raise EmptyListException('Новых статусов нет')
    else:
        return response.get('homeworks')[0]


def parse_status(homework):
    """Получение статуса домашней работы из ответа API."""
    if not homework:
        raise InvalidApiExc('Словарь homeworks пуст')
    if 'homework_name' not in homework:
        raise KeyError('Ключ homework_name отсутствует')
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    verdict = HOMEWORK_STATUSES[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверка наличия всех токенов в переменных окружения."""
    tokens = [PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]
    return False if None in tokens else True


def main():
    """Основная логика работы бота."""
    bot = Bot(token=TELEGRAM_TOKEN)
    current_timestamp = 1
    last_error = ''
    if not check_tokens():
        raise InvalidTokenException('Недоступны переменные окружения')
    while True:
        try:
            response = get_api_answer(current_timestamp)
            current_timestamp = response.get('current_date')
            homeworks = check_response(response)
            status = parse_status(homeworks)
            send_message(bot, status)
            time.sleep(RETRY_TIME)
        except EmptyListException:
            time.sleep(RETRY_TIME)
        except (InvalidApiExc, TypeError, KeyError, Exception) as error:
            message = f'Сбой в работе программы: {error}'
            if error != last_error:
                send_message(bot, message)
                last_error = error
                time.sleep(RETRY_TIME)
        # except TypeError as error:
        #     message = f'API не вернул словарь - {error}'
        #     if error != last_error:
        #         send_message(bot, message)
        #         last_error = error
        #         time.sleep(RETRY_TIME)
        # except KeyError as error:
        #     message = f'Ключ homework_name отсутствует - {error}'
        #     if error != last_error:
        #         send_message(bot, message)
        #         last_error = error
        #         time.sleep(RETRY_TIME)
        # except requests.Timeout as error:
        #     message = f'Сбой в работе программы: {error}'
        #     if error != last_error:
        #         send_message(bot, message)
        #         last_error = error
        #         time.sleep(RETRY_TIME)
        # except Exception as error:
        #     message = f'Сбой в работе программы: {error}'
        #     if error != last_error:
        #         send_message(bot, message)
        #         last_error = error
        #         time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
