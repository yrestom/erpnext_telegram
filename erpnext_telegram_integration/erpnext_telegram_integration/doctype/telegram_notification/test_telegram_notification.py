import frappe
import unittest
from unittest.mock import patch, MagicMock
from erpnext_telegram_integration.erpnext_telegram_integration.doctype.telegram_notification.telegram_notification import (
	run_telegram_notifications,
	evaluate_alert
)

class TestTelegramNotification(unittest.TestCase):
	def setUp(self):
		self.doctype = "Note"
		self.doc = frappe.get_doc({
			"doctype": "Note",
			"title": "Test Note",
			"content": "Test Content"
		}).insert()

	def tearDown(self):
		self.doc.delete()

	@patch("erpnext_telegram_integration.erpnext_telegram_integration.doctype.telegram_notification.telegram_notification.frappe.cache")
	@patch("erpnext_telegram_integration.erpnext_telegram_integration.doctype.telegram_notification.telegram_notification.frappe.get_all")
	def test_run_notifications_caching(self, mock_get_all, mock_cache):
		# Setup mock cache to return None (no alerts found yet)
		mock_cache().hget.return_value = None
		mock_get_all.return_value = []
		
		run_telegram_notifications(self.doc, "on_update")
		
		# Verify it tried to fetch from DB and then set cache
		mock_get_all.assert_called()
		mock_cache().hset.assert_called()

	@patch("erpnext_telegram_integration.erpnext_telegram_integration.doctype.telegram_notification.telegram_notification.frappe.get_doc")
	def test_evaluate_alert_condition(self, mock_get_doc):
		alert = MagicMock()
		alert.condition = "doc.title == 'Other Title'"
		alert.name = "Test Alert"
		
		# Condition fails, so send should NOT be called
		evaluate_alert(self.doc, alert, "Save")
		alert.send.assert_not_called()

		# Condition passes
		alert.condition = "doc.title == 'Test Note'"
		evaluate_alert(self.doc, alert, "Save")
		alert.send.assert_called_with(self.doc)

	@patch("erpnext_telegram_integration.erpnext_telegram_integration.doctype.telegram_notification.telegram_notification.frappe.enqueue")
	def test_async_send_enqueued(self, mock_enqueue):
		alert = frappe.get_doc({
			"doctype": "Telegram Notification",
			"subject": "Test Subject",
			"message": "Test Message",
			"document_type": "Note",
			"channel": "Telegram",
			"enabled": 1
		})
		
		# Test if send() enqueues the message
		alert.send(self.doc)
		
		mock_enqueue.assert_called_with(
			alert.send_a_telegram_msg,
			doc=self.doc,
			context=unittest.mock.ANY,
			queue="long",
			enqueue_after_commit=True
		)
