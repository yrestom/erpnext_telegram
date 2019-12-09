from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Settings"),
			"items": [
				{
					"type": "doctype",
					"name": "Telegram Settings",
				},
				{
					"type": "doctype",
					"name": "Telegram User Settings",
				},
				{
					"type": "doctype",
					"name": "Telegram Notification",
				},
				
			]
		},
		
		
	]
