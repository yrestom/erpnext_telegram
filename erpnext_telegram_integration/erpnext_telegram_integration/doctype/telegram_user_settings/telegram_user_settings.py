# -*- coding: utf-8 -*-
# Copyright (c) 2019, Youssef Restom and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import asyncio
import telegram
import binascii
import os
from frappe.model.document import Document
from frappe import _


class TelegramUserSettings(Document):
	

	def validate(self):
		pass


	def get_token_settings(self):
		return frappe.db.get_value('Telegram Settings', self.telegram_settings,'telegram_token')


	def get_chat_id(self):
		telegram_token = self.get_token_settings()
		bot = telegram.Bot(token = telegram_token)
		updates = bot.get_updates(limit=100)
		for u in updates:
			message = u.message.text
			chat_id = u.message.chat_id
			if self.telegram_token == message:
				self.telegram_chat_id = chat_id
				break
			else:
				self.telegram_chat_id = None




@frappe.whitelist()
def generate_telegram_token(is_group_chat):
	if int(is_group_chat) == 1:
		return "/"+ binascii.hexlify(os.urandom(19)).decode()
	else:
		return binascii.hexlify(os.urandom(20)).decode()

@frappe.whitelist()
def get_chat_id_button(telegram_token, telegram_settings):
	telegram_token_bot = frappe.db.get_value('Telegram Settings', telegram_settings,'telegram_token')
	chat_id = asyncio.run(get_chat_id(telegram_token_bot, telegram_token))
	if chat_id:
		return str(chat_id)
	else:
		frappe.msgprint(_("No chat id found for this token, please check the token and make sure you are pasting it in the right chat boot or group in telegram"))
	
async def get_chat_id(telegram_token_bot, telegram_token):
	bot = telegram.Bot(token = telegram_token_bot)
	async with bot:
		updates = await bot.get_updates(limit=100)
		for u in updates:
			# ignore messages without text
			if not u.message or not u.message.text :
				continue
			message = u.message.text
			chat_id = u.message.chat_id
			if telegram_token == message:
				print("chat_id >>>>>> "+ str(chat_id))
				return chat_id