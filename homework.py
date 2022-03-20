import logging
import os
import sys
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

import exception

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


def send_message(bot, message):
    """Send message in telegram chat."""
    try:
        logger.info('Отправление сообщения')
        bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message
        )
    except Exception:
        raise exception.SendMessageError(
            'Возникла ошибка при отпралении сообщения!'
        )


def get_api_answer(current_timestamp):
    """Make request to API."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}

    try:
        logging.info(
            f'Попытка сделать запрос к: {ENDPOINT}'
            f'с токеном: SECRET'
            f'с временной менткой: {params}'
        )
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
        if response.status_code != HTTPStatus.OK:
            raise ConnectionRefusedError('Указанный ресурс недоступен')
        return response.json()
    except Exception:
        raise ConnectionError('Возникла ошибка при обращении к API')


def check_response(response):
    """Check response API."""
    if not isinstance(response, dict):
        logging.error('Полученный ответ не является словарем')
        raise TypeError('Response не является словарем')
    elif 'homeworks' not in response:
        raise KeyError('Ключ homeworks не найден')
    elif 'current_date' not in response:
        raise KeyError('Ключ current_date не найден')
    elif not isinstance(response['homeworks'], list):
        raise TypeError('Получен не список')
    return response['homeworks']


def parse_status(homework):
    """Extract information about status of homework."""
    try:
        homework_name = homework.get('homework_name')
        homework_status = homework.get('status')
        verdict = HOMEWORK_STATUSES[homework_status]
        return f'Изменился статус проверки работы "{homework_name}". {verdict}'
    except LookupError:
        raise KeyError('Название не найдено')
    except LookupError:
        raise KeyError('Такого статуса не найдено')


def check_tokens():
    """Checking tokens."""
    tokens = [
        PRACTICUM_TOKEN,
        TELEGRAM_TOKEN,
        TELEGRAM_CHAT_ID
    ]
    return all(tokens)


def main():
    """Основная логика работы бота."""
    if check_tokens() is False:
        logger.critical(exception.TokenCheckError)
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    while True:
        try:
            response = get_api_answer(current_timestamp)
            response_check = check_response(response)
            if response_check:
                last_message = parse_status(response_check[0])
                send_message(bot, last_message)
            else:
                logger.debug('Нужно подождать')
            current_timestamp = response['current_date']
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(message)
            if message != last_message:
                send_message(bot, message)
                last_message = message
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s, %(levelname)s, %(name)s, %(message)s',
        handlers=[logging.StreamHandler(stream=sys.stdout)]
    )
    logger = logging.getLogger(__name__)
    main()
