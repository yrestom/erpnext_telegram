# Erpnext Telegram Integration And Notifications

Telegram Integration and Extra Notifications For Frappe & Erpnext to sending fast notifications for more productivity.



# Main features

### Telegram Notifications:

- Sending custom notification by Telegram Bots to Users, Employees, Customers, Suppliers or Students, and Telegram group chat.
- Sending Telegram direct messages from any form view.
- Multiple Telegram Bots channels.

### SMS Notifications:

- Sending custom notification by SMS to Users, Employees, Customers, Suppliers or Students .

### Date Notifications:

- Get alerts on important dates



# How to Install

1. `./env/bin/pip install python-telegram-bot --upgrade` "*This command is necessary to install the python-telegram-bot into bench environment. Otherwise, the pip3/pip command will install it in the python environment"*

2. `bench get-app erpnext_telegram_integration https://github.com/yrestom/erpnext_telegram.git`

3. `bench --site [your.site.name] install-app erpnext_telegram_integration`

4. `bench build`

5. `bench restart`

6. Create a new Telegram bot in `BotFather`

   For more reference :

   - [Bots: An introduction for developers](https://core.telegram.org/bots)
   - [Learn to build your first bot in Telegram with Python](https://www.freecodecamp.org/news/learn-to-build-your-first-bot-in-telegram-with-python-4c99526765e4/)

7. Get Telegram Bot Token from `BotFather`



# Setup and Use:

## Telegram Notifications:

In Erpnext Telegram Integration

1. Go to → Telegram Settings -> New Enter Telegram Bot Token

2. Go to → Telegram User Settings -> New to setup and define a new user setting

   1. Choose party.
   2. Choose Telegram User.
   3. Choose Telegram Settings.
   4. If it's a group check "Is Group Chat".
   5. Press "Generate Telegram Token" then the app will copy the "Telegram Token" to clipboard and will open a new window into the browser to the Bot web page.
   6. Paste "Telegram Token" in the Telegram Bot or if it is a Group Chat paste in the group after adding the Bot.
   7. Press "Get Chat ID" And if everything is ok it will get the chat ID.
   8. Press Save.

3. Go to → Telegram Notification -> New You can configure various notifications in your system to remind you of important activities. As the original [Erpnext Notification](https://erpnext.com/docs/user/manual/en/setting-up/notifications).

   Here chose the profile of "Telegram User Settings" want to send to him the notification or use the checkbox "Dynamic Recipients" to get the recipient from the DocType dynamically if it has a Link Field like "Customer", "Supplier", "Student" or "Employee", for this it needs to set up a "Telegram User Settings" for the customer, supplier ...

4. Also, you can send directly a Telegram message from any form view by going to the Menu and click "Send To Telegram".

5. When the app send a Telegram Notification it will write a new log into Extra Notifications > Extra Notification Log .



## SMS Notifications:

in Extra Notifications:

1. Go to → SMS Settings and set it up as [here](https://docs.erpnext.com/docs/user/manual/en/setting-up/sms-setting).

2. Go to → SMS Notification → New

   You can configure various notifications in your system to remind you of important activities. As the original [Erpnext Notification](https://erpnext.com/docs/user/manual/en/setting-up/notifications).

   Here chose the "Recipients" want to send to them the notification or use the checkbox "Dynamic Recipients" to get the recipient from the DocType dynamically if it has a Link Field like "Customer", "Supplier", "Student" or "Employee", for this it needs to set up a Contact for the customer, supplier..., and make sure the contact is related to the customer or supplier... and has Primary Mobile number as default.

3. Press Save.



## Date Notifications:

in Extra Notifications:

1. Go to → Date Notification → New.
2. Choose the DocType Name.
3. Press "Get Date Fields"
4. Choose the wanted fields an delete the rest.
5. Configure when the alert will be trigger by selecting "Days Before" or "Days After" and selecting a number of days for each field.
6. Configure the "Conditions" if need it.
7. Press Save.

When the Date Notification is trigger it will send an email to the related user and it will write a new log into Extra Notifications > Extra Notification Log .



## Dependencies

1. [Frappe](https://github.com/frappe/frappe) Version 12+
2. Python Version  3+
3. [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)



## License

MIT
