# Erpnext Telegram Integration

Telegram Integration For Frappe & Erpnext to sending fast Telegram notifications for more productivity.

## Main features

- Sending custom notification by Telegram Bots to users, employees, customers, and Telegram group chat.
- Sending Telegram direct messages from any form view.
- Multiple Telegram Bots channels.

## How to Install

### Install App

1. `./env/bin/pip install python-telegram-bot --upgrade`
2. `bench get-app erpnext_telegram_integration [https://github.com/yrestom/erpnext_telegram](https://github.com/yrestom/erpnext_telegram)`
3. `bench install-app erpnext_telegram_integration`
4. `bench build`
5. `bench restart`
6. Create a new Telegram bot in `BotFather`

    For more reference :

    - [Bots: An introduction for developers](https://core.telegram.org/bots)
    - [Learn to build your first bot in Telegram with Python](https://www.freecodecamp.org/news/learn-to-build-your-first-bot-in-telegram-with-python-4c99526765e4/)
7. Get Telegram Bot Token from `BotFather`

### In Erpnext Telegram Integration

1. Go to -> Telegram Settings -> New
Enter Telegram Bot Token
2. Go to -> Telegram User Settings -> New
to setup and define a new user setting
    1. choose party
    2. choose Telegram User
    3. choose Telegram Settings
    4. if is a group check "Is Group Chat"
    5. press "Generat Telegram Token"
    6. copy "Telegram Token" and past it in the Telgram Bot
    or if is a Group Chat past in the group after add the Bot
    7. press "Get Chat ID"
    if everything is ok it will get the chat ID
    8. press Save
3. Go to -> Telegram Notification -> New
Here you can configure various notifications in your system to remind you of important activities.
As the original [Erpnext Notification](https://erpnext.com/docs/user/manual/en/setting-up/notifications)
4. Also, you can send directly a Telegram message from any form view by going to the Menu and click "Send To Telegram".

### Dependencies

1. [Frappe](https://github.com/frappe/frappe)
2. [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) 

### License

MIT
