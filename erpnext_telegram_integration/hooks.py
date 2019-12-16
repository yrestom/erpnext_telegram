# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "erpnext_telegram_integration"
app_title = "Erpnext Telegram Integration"
app_publisher = "Youssef Restom"
app_description = "Telegram Integration For Frappe - Erpnext"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "youssef@totrox.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/erpnext_telegram_integration/css/erpnext_telegram_integration.css"
# app_include_js = "/assets/erpnext_telegram_integration/js/erpnext_telegram_integration.js"
app_include_js = "/assets/js/erpnext_telegram_integration.min.js"



# include js, css files in header of web template
# web_include_css = "/assets/erpnext_telegram_integration/css/erpnext_telegram_integration.css"
# web_include_js = "/assets/erpnext_telegram_integration/js/erpnext_telegram_integration.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
## doctype_js = {"Quote" : "public/js/send_to_telegram.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "erpnext_telegram_integration.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "erpnext_telegram_integration.install.before_install"
# after_install = "erpnext_telegram_integration.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "erpnext_telegram_integration.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }
doc_events = {

     "*": {
                "validate": "erpnext_telegram_integration.erpnext_telegram_integration.doctype.telegram_notification.telegram_notification.run_telegram_notifications",
                "onload": "erpnext_telegram_integration.erpnext_telegram_integration.doctype.telegram_notification.telegram_notification.run_telegram_notifications",
                "before_insert": "erpnext_telegram_integration.erpnext_telegram_integration.doctype.telegram_notification.telegram_notification.run_telegram_notifications",
                "after_insert": "erpnext_telegram_integration.erpnext_telegram_integration.doctype.telegram_notification.telegram_notification.run_telegram_notifications",
                "before_naming": "erpnext_telegram_integration.erpnext_telegram_integration.doctype.telegram_notification.telegram_notification.run_telegram_notifications",
                "before_change": "erpnext_telegram_integration.erpnext_telegram_integration.doctype.telegram_notification.telegram_notification.run_telegram_notifications",
                "before_update_after_submit": "erpnext_telegram_integration.erpnext_telegram_integration.doctype.telegram_notification.telegram_notification.run_telegram_notifications",
                "before_validate": "erpnext_telegram_integration.erpnext_telegram_integration.doctype.telegram_notification.telegram_notification.run_telegram_notifications",
                "before_save": "erpnext_telegram_integration.erpnext_telegram_integration.doctype.telegram_notification.telegram_notification.run_telegram_notifications",
                "autoname": "erpnext_telegram_integration.erpnext_telegram_integration.doctype.telegram_notification.telegram_notification.run_telegram_notifications", 
		"on_update": "erpnext_telegram_integration.erpnext_telegram_integration.doctype.telegram_notification.telegram_notification.run_telegram_notifications",
		"on_cancel": "erpnext_telegram_integration.erpnext_telegram_integration.doctype.telegram_notification.telegram_notification.run_telegram_notifications",
		"on_trash": "erpnext_telegram_integration.erpnext_telegram_integration.doctype.telegram_notification.telegram_notification.run_telegram_notifications",
		"on_submit": "erpnext_telegram_integration.erpnext_telegram_integration.doctype.telegram_notification.telegram_notification.run_telegram_notifications",
		"on_update_after_submit": "erpnext_telegram_integration.erpnext_telegram_integration.doctype.telegram_notification.telegram_notification.run_telegram_notifications",
                "on_change": "erpnext_telegram_integration.erpnext_telegram_integration.doctype.telegram_notification.telegram_notification.run_telegram_notifications",
	},


}
# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"erpnext_telegram_integration.tasks.all"
# 	],
# 	"daily": [
# 		"erpnext_telegram_integration.tasks.daily"
# 	],
# 	"hourly": [
# 		"erpnext_telegram_integration.tasks.hourly"
# 	],
# 	"weekly": [
# 		"erpnext_telegram_integration.tasks.weekly"
# 	]
# 	"monthly": [
# 		"erpnext_telegram_integration.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "erpnext_telegram_integration.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "erpnext_telegram_integration.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "erpnext_telegram_integration.task.get_dashboard_data"
# }

