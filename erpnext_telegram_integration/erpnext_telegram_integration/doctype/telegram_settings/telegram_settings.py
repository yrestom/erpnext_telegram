# -*- coding: utf-8 -*-
# Copyright (c) 2019, Youssef Restom and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import telegram
from frappe.model.document import Document
from frappe.utils import get_url_to_form
from frappe import _
from frappe.utils.print_format import download_pdf

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
			if attachment:
				attachment_url =get_url_for_telegram(reference_doctype, reference_name)
				message = message + space +  attachment_url
			bot.send_message(chat_id=telegram_chat_id, text=message)
		
	else:
		message = space + str(message) + space
		bot.send_message(chat_id=telegram_chat_id, text=message)



def get_url_for_telegram(doctype, name):
	doc = frappe.get_doc(doctype, name)
	return "{url}/api/method/erpnext_telegram_integration.get_pdf.pdf?doctype={doctype}&name={name}&key={key}".format(
		url=frappe.utils.get_url(),
		doctype=doctype,
		name=name,
		key=doc.get_signature()
	).replace(" ", "%20")


