from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils.print_format import download_pdf


@frappe.whitelist(allow_guest=True)
def pdf(doctype, name, key):
	doc = frappe.get_doc(doctype, name)
	if not key == doc.get_signature():
		return 403
	download_pdf(doctype, name, format=None, doc=None, no_letterhead=0)