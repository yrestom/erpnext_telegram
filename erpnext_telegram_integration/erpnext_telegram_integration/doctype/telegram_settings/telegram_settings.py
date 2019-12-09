# -*- coding: utf-8 -*-
# Copyright (c) 2019, Youssef Restom and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import telegram
from frappe.model.document import Document
from frappe.utils import get_url_to_form
from frappe import _

class TelegramSettings(Document):
	pass



@frappe.whitelist()
def send_to_telegram(telegram_user, message, reference_doctype=None, reference_name=None, attachment=None):

	space = "\n" * 2
	telegram_chat_id = frappe.db.get_value('Telegram User Settings', telegram_user,'telegram_chat_id')
	telegram_settings = frappe.db.get_value('Telegram User Settings', telegram_user,'telegram_settings')
	telegram_token = frappe.db.get_value('Telegram Settings', telegram_settings,'telegram_token')
	bot = telegram.Bot(token=telegram_token)


	if reference_doctype and reference_name:
		doc_url = get_url_to_form(reference_doctype, reference_name)
		telegram_doc_link = _("See the document at {0}").format(doc_url)
		if message:
			message = space + str(message) + space + str(telegram_doc_link)
			bot.send_message(chat_id=telegram_chat_id, text=message)
		
	else:
		message = space + str(message) + space
		bot.send_message(chat_id=telegram_chat_id, text=message)

	if attachment:
		## attached_file must be url  'tests/telegram.ogg'
		bot.send_document(chat_id=telegram_chat_id, document=open(attachment, 'rb'))
		
	
