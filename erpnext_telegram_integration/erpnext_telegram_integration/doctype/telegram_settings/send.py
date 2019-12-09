# -*- coding: utf-8 -*-
# Copyright (c) 2019, Youssef Restom and contributors
# For license information, please see license.txt

from __future__ import unicode_literals 
import frappe
import telegram
from frappe.model.document import Document
from frappe.utils import get_url_to_form
from frappe import _
import json
from werkzeug import url_fix
from six.moves.urllib.parse import quote, urlencode, urlparse

class ToObject(object):
    def __init__(self, data):
	    self.__dict__ = json.loads(data)

#'https://erp.totrox.com/api/method/erpnext_telegram_integration.erpnext_telegram_integration.doctype.telegram_settings.send.send'
@frappe.whitelist(allow_guest=True)
def send(*args, **kwargs):
	
	r = frappe.request
	uri = url_fix(r.url.replace("+"," "))
	http_method = r.method
	body = r.get_data()
	headers = r.headers

	space = "\n" * 2
	message = ""

	if body :
		data = body.decode('utf-8')
		msgs =  ToObject(data)
		atr_list = list(msgs.__dict__)

		for atr in atr_list:
			if getattr(msgs, atr) :
				message = message + atr + ":  " +  getattr(msgs, atr) + space
				
		headers_list = list(headers)
		message = str(headers_list[0]) +space + message
		
	else:
		message = headers

	telegram_chat_id = frappe.db.get_value('Telegram User Settings', "ahmed@ahmed.com-ErpTotorxBot",'telegram_chat_id')
	telegram_settings = frappe.db.get_value('Telegram User Settings', "ahmed@ahmed.com-ErpTotorxBot",'telegram_settings')
	telegram_token = frappe.db.get_value('Telegram Settings', telegram_settings,'telegram_token')
	bot = telegram.Bot(token=telegram_token)


	message = space + str(message) + space
	bot.send_message(chat_id=telegram_chat_id, text=message)
