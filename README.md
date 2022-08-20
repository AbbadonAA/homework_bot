# Homework Bot

## Описание

Учебный проект по созданию Телеграм-бота, опрашивающего API сервиса Практикум.Домашка и проверяющего статус отправленной на ревью домашней работы.

При изменении статуса бот анализирует ответ API и отправляет соответствующее уведомление в Telegram.

Телеграм-бот запущен на облачной платформе Heroku.

:exclamation: Запустить бота сможет только студент Яндекс.Практикума, т.к. для запуска требуется получить токен сервиса Практикум.Домашка.

## Установка:
1. Клонируйте репозиторий:
```
git clone git@github.com:AbbadonAA/homework_bot.git
```
2. Создайте и активируйте виртуальное окружение:
```
python3 -m venv venv
source venv/bin/activate
```
3. Установите зависимости:
```
pip install -r requirements.txt
```
4. При помощи @BotFather в Telegram создайте нового бота и получите API TOKEN
5. Получите токен сервиса Практикум.Домашка (PR TOKEN) по адресу:
   
   https://oauth.yandex.ru/authorize?response_type=token&client_id=1d0b9dd4d652455a9eb710d450ff456a
6. При помощи @userinfobot получите (команда - "me") TELEGRAM CHAT ID
7. В корневой директории создайте файл .env со следующим содержанием:
```
PR_TOKEN=<PR TOKEN>
MY_TOKEN=<API TOKEN>
CHAT_ID=<TELEGRAM CHAT ID>
```
6. В корневой директории выполните команду для запуска бота:
```
python homework.py
```
7. Бот запущен и отслеживает изменения статуса проверки домашней работы.

### Автор
Pushkarev Anton

pushkarevantona@gmail.com
