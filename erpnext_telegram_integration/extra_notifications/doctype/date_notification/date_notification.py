# -*- coding: utf-8 -*-
# Copyright (c) 2020, Youssef Restom and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import nowdate, add_to_date
from jinja2 import TemplateError

class DateNotification(Document):

	def validate(self):
		self.validate_condition()
		

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
		if not self.enable:
			return docs
		for row_date_field in self.date_fields:
			if not int(row_date_field.enable):
				continue
			diff_days = int(row_date_field.days)
			if row_date_field.days_before_or_after=="Days After":
				diff_days = -diff_days
			
			reference_date = add_to_date(nowdate(), days=diff_days)
			reference_date_start = reference_date + ' 00:00:00.000000'
			reference_date_end = reference_date + ' 23:59:59.000000'
			if not row_date_field.doctype_name:
				continue
			doc_list = frappe.get_all(row_date_field.doctype_name,
				fields='name',
				filters=[
					{ row_date_field.fieldname: ('>=', reference_date_start) },
					{ row_date_field.fieldname: ('<=', reference_date_end) },
				])
			child_doctype_name = ""
			for d in doc_list:
				if int(row_date_field.is_child_field) == 0:
					doc = frappe.get_doc(row_date_field.doctype_name, d.name)
					date_value = str(getattr(doc,row_date_field.fieldname))
				else :
					child_doc = frappe.get_doc(row_date_field.doctype_name, d.name)
					date_value = str(getattr(child_doc,row_date_field.fieldname))
					child_doctype_name = str(child_doc.doctype)
					doc = frappe.get_doc(child_doc.parenttype, child_doc.parent)
					

				if self.condition and not frappe.safe_eval(self.condition, None, get_context(doc)):
					continue

				doc.child_doctype_name = child_doctype_name 
				doc.date_value = date_value
				doc.date_notification = {
					"label": row_date_field.label,
					"fieldname": row_date_field.fieldname,
					"days_before_or_after": row_date_field.days_before_or_after,
					"days" : row_date_field.days
				}
				docs.append(doc)
				
		return docs



	def creat_extra_notification_log(self, doc):
		child_doctype_name = _(doc.child_doctype_name)+ " "
		date_value = doc.date_value
		enl_doc = frappe.new_doc('Extra Notification Log')
		enl_doc.subject = _(doc.doctype) +" "+_(doc.name) +" "+ child_doctype_name + _(doc.date_notification["label"]) +" "+ date_value
		enl_doc.doctype_name = doc.doctype
		enl_doc.doc_name = doc.name
		enl_doc.status = "Open"
		enl_doc.type = "Date"
		enl_doc.doc_name = doc.name
		enl_doc.message = child_doctype_name + _(doc.date_notification["label"]) + " " + date_value

		enl_doc.insert(ignore_permissions=True)


def get_context(doc):
	return {"doc": doc, "nowdate": nowdate, "frappe.utils": frappe.utils}

@frappe.whitelist()
def get_date_fields(doctype_name):
	fields = frappe.get_meta(doctype_name).fields
	filed_list = []
	for d in fields:
		if d.fieldtype == "Date" or d.fieldtype == "Datetime":
			field = {	
				"label":d.label,
				"fieldname": d.fieldname,
				"fieldtype" : d.fieldtype,
				"doctype_name": doctype_name,
			}
			filed_list.append(field)
		if d.fieldtype == "Table":
			child_fields = frappe.get_meta(d.options).fields
			for c in child_fields:
				if c.fieldtype == "Date" or c.fieldtype == "Datetime":
					field = {	
						"label":c.label,
						"fieldname": c.fieldname,
						"fieldtype" : c.fieldtype,
						"is_child_field": 1,
						"doctype_name": d.options,
						# "child_doctype_name": c.name,
						"c":c,
					}
					filed_list.append(field)
	return filed_list


@frappe.whitelist()
def get_documents_for_today(notification):
	notification = frappe.get_doc('Date Notification', notification)
	notification.check_permission('read')
	return [d.name for d in notification.get_documents_for_today()]


@frappe.whitelist()
def trigger_daily_alerts():
	if frappe.flags.in_import or frappe.flags.in_patch:
		# don't send notifications while syncing or patching
		return

	doc_list = frappe.get_all('Date Notification',
		filters={
			'enable': 1
		})

	for d in doc_list:
		alert = frappe.get_doc('Date Notification', d.name)

		for doc_obj in alert.get_documents_for_today():
			evaluate_alert(doc_obj, alert)
			frappe.db.commit()


def evaluate_alert(doc, alert):
	try:
		context = get_context(doc)
		if alert.condition:
			if not frappe.safe_eval(alert.condition, None, context):
				return
		alert.creat_extra_notification_log(doc)
	except TemplateError:
		frappe.throw(_("Error while evaluating Notification {0}. Please fix your template.").format(alert))
	except Exception as e:
		error_log = frappe.log_error(message=frappe.get_traceback(), title=str(e))
		frappe.throw(_("Error in Notification: {}".format(
			frappe.utils.get_link_to_form('Error Log', error_log.name))))