from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
	
		{
			"label": _("SMS Notifications"),
			"items": [
				{
					"type": "doctype",
					"name": "SMS Settings",
					"onboard": 1,
				},
				{
					"type": "doctype",
					"name": "SMS Notification",
					"onboard": 1,
				},
				
			]
		},
		
		
	]
