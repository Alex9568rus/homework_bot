#  Telgram-bot

## Описание проекта  

Telegram-бот, работающий с API сервиса Практикум.Домашка и отправляющий сообщение о статусе проверки последней домашней работы студенту в чат бота. В проекте применяется логирование, обработка исключений при доступе к внешним сетевым ресурсам, конфиденциальные данные хранятся в пространстве переменных окружения.

-----
## Стек технологий

* Python 3.8
* Telegram Bot API

-----
## Установка проекта

1. Клонировать репозиторий и перейти в него
* `git clone git@github.com:Alex9568rus/homework_bot.git`
* `cd homework_bot`

2. Установить окружение и зависимости
* `python3 -m venv venv`
* `source venv/bin/activate`
* `python3 -m pip install --upgrade pip`
* `pip install -r requirements.txt`

3. Создать файл виртуального окружения .env в корневой директории проекта и прописать токены в следующем формате:
  ```
  sudo nano .env
  
  PRACTICUM_TOKEN=<ваш_токен_Практикум.Домашка>
  TELEGRAM_TOKEN=<токен_телеграм_бота>
  TELEGRAM_CHAT_ID=<id_чата>
  ```
4. Запустить проект  
`python3 homework.py`
