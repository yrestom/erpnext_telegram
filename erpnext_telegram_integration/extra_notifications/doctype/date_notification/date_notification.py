# -*- coding: utf-8 -*-
# Copyright (c) 2020, Youssef Restom and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import nowdate, parse_val, is_html, add_to_date
from frappe.modules.utils import export_module_json, get_doc_module
from six import string_types

class DateNotification(Document):
	def validate(self):
		self.validate_condition()
		# self.print_today_docs_list()
		

	def validate_condition(self):
		temp_doc = frappe.new_doc(self.doctype_name)
		if self.condition:
			try:
				frappe.safe_eval(self.condition, None, get_context(temp_doc))
			except Exception:
				frappe.throw(_("The Condition '{0}' is invalid").format(self.condition))


	def get_documents_for_today(self):
		'''get list of documents that will be triggered today'''
		docs = []
		for row_date_field in self.date_fields:
			diff_days = int(row_date_field.days)
			if row_date_field.days_before_or_after=="Days After":
				diff_days = -diff_days
			
			reference_date = add_to_date(nowdate(), days=diff_days)
			reference_date_start = reference_date + ' 00:00:00.000000'
			reference_date_end = reference_date + ' 23:59:59.000000'

			doc_list = frappe.get_all(self.doctype_name,
				fields='name',
				filters=[
					{ row_date_field.fieldname: ('>=', reference_date_start) },
					{ row_date_field.fieldname: ('<=', reference_date_end) }
				])

			for d in doc_list:
				doc = frappe.get_doc(self.doctype_name, d.name)

				if self.condition and not frappe.safe_eval(self.condition, None, get_context(doc)):
					continue
				docs.append(doc)

		return docs


	def print_today_docs_list(self):
		docs_dict = self.get_documents_for_today()
		for doc in docs_dict:
			frappe.msgprint(str(doc.name))








def get_context(doc):
	return {"doc": doc, "nowdate": nowdate, "frappe.utils": frappe.utils}

@frappe.whitelist()
def get_date_fields(doctype_name):
	fields = frappe.get_doc("DocType", doctype_name).fields
	filed_list = []
	for d in fields:
		if d.fieldtype == "Date" or d.fieldtype == "Datetime":
			field = {	
				"label":d.label,
				"fieldname": d.fieldname,
				"fieldtype" : d.fieldtype,
			}
			filed_list.append(field)
	return filed_list


@frappe.whitelist()
def get_documents_for_today(notification):
	notification = frappe.get_doc('Date Notification', notification)
	notification.check_permission('read')
	return [d.name for d in notification.get_documents_for_today()]