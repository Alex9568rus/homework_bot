import logging
import os
import sys
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


logger = logging.getLogger(__name__)
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format='%(asctime)s, %(level_name)s, %(name)s, %(message)s'
)
logger.addHandler(logging.StreamHandler())


def send_message(bot, message):
    """Send message in telegram chat."""
    try:
        logging.info('Отправление сообщения')
        bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message
        )
    except Exception as error:
        logging.error(error)
        raise Exception('Возникла ошибка при отпралении сообщения!')


def get_api_answer(current_timestamp):
    """Make request to API."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}

    try:
        logging.info('Попытка сделать запрос')
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
        if response.status_code != HTTPStatus.OK:
            logging.error('Указанный ресурс недоступен')
            raise Exception('Указанный ресурс недоступен')
    except Exception as error:
        logging.error(error)
        raise Exception('Возникла ошибка при обращении к указанному API')

    return response.json()


def check_response(response):
    """Check response API."""
    if not isinstance(response, dict):
        logging.error('Полученный ответ не является словарем')
        raise TypeError('Response не является словарем')
    elif 'homeworks' not in response:
        logging.error('Ключ homeworks не найден')
        raise KeyError('Ключ homeworks не найден')
    elif type(response['homeworks']) != list:
        logging.error('Необходимо получить список')
        raise TypeError('Получен не список')
    return response['homeworks']


def parse_status(homework):
    """Extract information about status of homework."""
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if homework_status not in HOMEWORK_STATUSES:
        logging.error('Недоступный статус')
        raise KeyError('Такого статуса не найдено')
    verdict = HOMEWORK_STATUSES[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Checking tokens."""
    if PRACTICUM_TOKEN and TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        return True
    else:
        logging.critical('Ошибка при проверке значений токенов')
        return False


def main():
    """Основная логика работы бота."""
    start_status = None
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    while True:
        try:
            response = get_api_answer(current_timestamp)
            response_check = check_response(response)
            if start_status != response_check[0].get('status'):
                send_message(bot, parse_status(response_check[0]))
                start_status = response_check[0].get('status')
            else:
                logger.debug('Нужно подождать')
            current_timestamp = response['current_date']
            time.sleep(RETRY_TIME)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.error(message)
            send_message(bot, message)
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
