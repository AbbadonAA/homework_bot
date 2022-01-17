import os
from dotenv import load_dotenv
import requests
import time
from telegram import Bot

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PR_TOKEN')
TELEGRAM_TOKEN = os.getenv('MY_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('CHAT_ID')

RETRY_TIME = 600
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
    try:
        homework_statuses = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params=params
        )
    except Exception as error:
        raise ValueError(f'Ошибка при запросе к API - {error}')
    if homework_statuses.status_code != 200:
        print(homework_statuses.status_code)
        homework_statuses.raise_for_status()
    return homework_statuses.json()


def check_response(response):
    """Проверка ответа API и возврат списка работ."""
    if type(response) is not dict:
        raise TypeError('Некорректный тип данных')
    if len(response) != 2:
        raise ValueError('Некорректный ответ API')
    elif type(response.get('homeworks')) is not list:
        raise ValueError('Некорректный тип данных')
    else:
        return response.get('homeworks')


def parse_status(homework):
    """."""
    if homework:
        if 'homework_name' or 'status' not in homework[0]:
            raise KeyError('Ошибка - отсутствие значений')
        homework_name = homework[0].get('homework_name')
        homework_status = homework[0].get('status')
        if homework_status not in HOMEWORK_STATUSES:
            raise KeyError('Некорректный статус')
        verdict = HOMEWORK_STATUSES[homework_status]
        return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверка наличия всех токенов в переменных окружения."""
    tokens = [PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]
    return False if None in tokens else True


def main():
    """Основная логика работы бота."""
    bot = Bot(token=TELEGRAM_TOKEN)
    message = 'Я работаю'
    send_message(bot, message)
    # current_timestamp = int(time.time())

    # ...

    # while True:
    #     try:
    #         response = ...

    #         ...

    #         current_timestamp = ...
    #         time.sleep(RETRY_TIME)

    #     except Exception as error:
    #         message = f'Сбой в работе программы: {error}'
    #         ...
    #         time.sleep(RETRY_TIME)
    #     else:
    #         ...


if __name__ == '__main__':
    main()
