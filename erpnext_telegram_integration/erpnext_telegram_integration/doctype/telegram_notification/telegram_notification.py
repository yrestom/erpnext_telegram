# -*- coding: utf-8 -*-
# Copyright (c) 2019, Youssef Restom and contributors
# For license information, please see license.txt
from __future__ import unicode_literals
import frappe
import json, os
from frappe import _
from frappe.model.document import Document

# from frappe.core.doctype.role.role import get_emails_from_role
from frappe.utils import (
    validate_email_address,
    nowdate,
    parse_val,
    is_html,
    add_to_date,
)
from frappe.utils.jinja import validate_template
from frappe.modules.utils import export_module_json, get_doc_module
from six import string_types
from erpnext_telegram_integration.erpnext_telegram_integration.doctype.telegram_settings.telegram_settings import (
    send_to_telegram,
)


class TelegramNotification(Document):
    def onload(self):
        """load message"""
        if self.is_standard:
            self.message = self.get_template()

    def autoname(self):
        if not self.name:
            self.name = self.subject

    def validate(self):
        validate_template(self.subject)
        validate_template(self.message)

        if self.event in ("Days Before", "Days After") and not self.date_changed:
            frappe.throw(_("Please specify which date field must be checked"))

        if self.event == "Value Change" and not self.value_changed:
            frappe.throw(_("Please specify which value field must be checked"))

        self.validate_forbidden_types()
        self.validate_condition()
        self.validate_standard()
        frappe.cache().hdel("tel_notifications", self.document_type)

    def on_update(self):
        path = export_module_json(self, self.is_standard, self.module)
        if path:
            # js
            if not os.path.exists(path + ".md") and not os.path.exists(path + ".html"):
                with open(path + ".md", "w") as f:
                    f.write(self.message)

            # py
            if not os.path.exists(path + ".py"):
                with open(path + ".py", "w") as f:
                    f.write(
                        """from __future__ import unicode_literals

import frappe

def get_context(context):
	# do your magic here
	pass
"""
                    )

    def validate_standard(self):
        if self.is_standard and not frappe.conf.developer_mode:
            frappe.throw(
                _(
                    "Cannot edit Standard Notification. To edit, please disable this and duplicate it"
                )
            )

    def validate_condition(self):
        temp_doc = frappe.new_doc(self.document_type)
        if self.condition:
            try:
                frappe.safe_eval(self.condition, None, get_context(temp_doc))
            except Exception:
                frappe.throw(_("The Condition '{0}' is invalid").format(self.condition))

    def validate_forbidden_types(self):
        forbidden_document_types = ("Email Queue",)
        if (
            self.document_type in forbidden_document_types
            or frappe.get_meta(self.document_type).istable
        ):
            # currently notifications don't work on child tables as events are not fired for each record of child table

            frappe.throw(
                _("Cannot set Notification on Document Type {0}").format(
                    self.document_type
                )
            )

    def get_documents_for_today(self):
        """get list of documents that will be triggered today"""
        docs = []

        diff_days = self.days_in_advance
        if self.event == "Days After":
            diff_days = -diff_days

        reference_date = add_to_date(nowdate(), days=diff_days)
        reference_date_start = reference_date + " 00:00:00.000000"
        reference_date_end = reference_date + " 23:59:59.000000"

        doc_list = frappe.get_all(
            self.document_type,
            fields="name",
            filters=[
                {self.date_changed: (">=", reference_date_start)},
                {self.date_changed: ("<=", reference_date_end)},
            ],
        )

        for d in doc_list:
            doc = frappe.get_doc(self.document_type, d.name)

            if self.condition and not frappe.safe_eval(
                self.condition, None, get_context(doc)
            ):
                continue

            docs.append(doc)

        return docs

    def send(self, doc):
        """Build recipients and send Notification"""

        context = get_context(doc)
        context = {"doc": doc, "alert": self, "comments": None}
        if doc.get("_comments"):
            context["comments"] = json.loads(doc.get("_comments"))

        if self.is_standard:
            self.load_standard_properties(context)

        if self.channel == "Telegram":
            self.send_a_telegram_msg(doc, context)

        if self.set_property_after_alert:
            allow_update = True
            if (
                doc.docstatus == 1
                and not doc.meta.get_field(
                    self.set_property_after_alert
                ).allow_on_submit
            ):
                allow_update = False

            if allow_update:
                frappe.db.set_value(
                    doc.doctype,
                    doc.name,
                    self.set_property_after_alert,
                    self.property_value,
                    update_modified=False,
                )
                doc.set(self.set_property_after_alert, self.property_value)

    def get_dynamic_recipients(self, doc):
        recipients_telegram_user_list = []
        field_names = ["Customer", "Supplier", "Student", "Employee", "User"]
        if self.dynamic_recipients:
            fields = get_doc_fields(self.document_type)
            for d in fields:
                party = d.get("field_options")
                if not party:
                    if (
                        d.get("field_get_value")
                        and doc.get(d["field_get_value"]) in field_names
                    ):
                        party = doc.get(d["field_get_value"])
                    else:
                        break

                filters = (
                    {
                        "party": party,
                        "telegram_user": doc.get(d["fieldname"]),
                    },
                )
                telegram_user_list = frappe.get_all(
                    "Telegram User Settings",
                    filters=filters,
                    fields=["name", "telegram_settings", "telegram_user"],
                )
                for i in telegram_user_list:
                    recipients_telegram_user_list.append(i.name)
        return recipients_telegram_user_list

    def send_a_telegram_msg(self, doc, context):
        recipients_telegram_user_list = []
        if self.telegram_user:
            recipients_telegram_user_list.append(self.telegram_user)
        recipients_telegram_user_list.extend(self.get_dynamic_recipients(doc))
        space = "\n" * 2
        message = frappe.render_template(self.subject, context) + space
        message = message + frappe.render_template(self.message, context)
        attachment = self.get_attachment(doc)
        for telegram_user in recipients_telegram_user_list:
            send_to_telegram(
                telegram_user=telegram_user,
                message=message,
                reference_doctype=doc.doctype,
                reference_name=doc.name,
                attachment=attachment,
            )

            doc.message_notification = message
            doc.from_user = frappe.session.user
            doc.party_type = frappe.get_value(
                "Telegram User Settings", telegram_user, "party"
            )
            doc.to_party = frappe.get_value(
                "Telegram User Settings", telegram_user, "telegram_user"
            )
            creat_extra_notification_log(doc)

    def get_attachment(self, doc):
        """ check print settings are attach the pdf """
        if not self.attach_print:
            return None

        print_settings = frappe.get_doc("Print Settings", "Print Settings")
        if (doc.docstatus == 0 and not print_settings.allow_print_for_draft) or (
            doc.docstatus == 2 and not print_settings.allow_print_for_cancelled
        ):

            # ignoring attachment as draft and cancelled documents are not allowed to print
            status = "Draft" if doc.docstatus == 0 else "Cancelled"
            frappe.throw(
                _(
                    """Not allowed to attach {0} document,
				please enable Allow Print For {0} in Print Settings""".format(
                        status
                    )
                ),
                title=_("Error in Notification"),
            )
        else:
            return [
                {
                    "print_format_attachment": 1,
                    "doctype": doc.doctype,
                    "name": doc.name,
                    "print_format": self.print_format,
                    "print_letterhead": print_settings.with_letterhead,
                    "lang": frappe.db.get_value(
                        "Print Format", self.print_format, "default_print_language"
                    )
                    if self.print_format
                    else "en",
                }
            ]

    def get_template(self):
        module = get_doc_module(self.module, self.doctype, self.name)

        def load_template(extn):
            template = ""
            template_path = os.path.join(
                os.path.dirname(module.__file__), frappe.scrub(self.name) + extn
            )
            if os.path.exists(template_path):
                with open(template_path, "r") as f:
                    template = f.read()
            return template

        return load_template(".html") or load_template(".md")

    def load_standard_properties(self, context):
        """load templates and run get_context"""
        module = get_doc_module(self.module, self.doctype, self.name)
        if module:
            if hasattr(module, "get_context"):
                out = module.get_context(context)
                if out:
                    context.update(out)

        self.message = self.get_template()

        if not is_html(self.message):
            self.message = frappe.utils.md_to_html(self.message)


@frappe.whitelist()
def run_telegram_notifications(doc, method):
    """Run notifications for this method"""
    if frappe.flags.in_import or frappe.flags.in_patch or frappe.flags.in_install:
        return

    if doc.flags.tel_notifications_executed == None:
        doc.flags.tel_notifications_executed = []

    if doc.flags.tel_notifications == None:
        alerts = frappe.cache().hget("tel_notifications", doc.doctype)
        if alerts == None:
            alerts = frappe.get_all(
                "Telegram Notification",
                fields=["name", "event", "method"],
                filters={"enabled": 1, "document_type": doc.doctype},
            )
            frappe.cache().hset("tel_notifications", doc.doctype, alerts)
        doc.flags.tel_notifications = alerts

    if not doc.flags.tel_notifications:
        return

    def _evaluate_alert(alert):
        if not alert.name in doc.flags.tel_notifications_executed:
            evaluate_alert(doc, alert.name, alert.event)
            doc.flags.tel_notifications_executed.append(alert.name)

    event_map = {
        "on_update": "Save",
        "after_insert": "New",
        "on_submit": "Submit",
        "on_cancel": "Cancel",
    }

    if not doc.flags.in_insert:
        # value change is not applicable in insert
        event_map["validate"] = "Value Change"
        event_map["before_change"] = "Value Change"
        event_map["before_update_after_submit"] = "Value Change"

    for alert in doc.flags.tel_notifications:
        event = event_map.get(method, None)
        if event and alert.event == event:
            _evaluate_alert(alert)
        elif alert.event == "Method" and method == alert.method:
            _evaluate_alert(alert)


@frappe.whitelist()
def get_documents_for_today(notification):
    notification = frappe.get_doc("Telegram Notification", notification)
    notification.check_permission("read")
    return [d.name for d in notification.get_documents_for_today()]


def trigger_daily_alerts():
    trigger_notifications(None, "daily")


def trigger_notifications(doc, method=None):
    if frappe.flags.in_import or frappe.flags.in_patch:
        # don't send notifications while syncing or patching
        return

    if method == "daily":
        doc_list = frappe.get_all(
            "Telegram Notification",
            filters={"event": ("in", ("Days Before", "Days After")), "enabled": 1},
        )
        for d in doc_list:
            alert = frappe.get_doc("Telegram Notification", d.name)

            for doc in alert.get_documents_for_today():
                evaluate_alert(doc, alert, alert.event)
                frappe.db.commit()


def evaluate_alert(doc, alert, event):
    from jinja2 import TemplateError

    try:
        if isinstance(alert, string_types):
            alert = frappe.get_doc("Telegram Notification", alert)

        context = get_context(doc)

        if alert.condition:
            if not frappe.safe_eval(alert.condition, None, context):
                return

        if event == "Value Change" and not doc.is_new():
            try:
                db_value = frappe.db.get_value(
                    doc.doctype, doc.name, alert.value_changed
                )
            except Exception as e:
                if frappe.db.is_missing_column(e):
                    alert.db_set("enabled", 0)
                    frappe.log_error(
                        "Notification {0} has been disabled due to missing field".format(
                            alert.name
                        )
                    )
                    return
                else:
                    raise
            db_value = parse_val(db_value)
            if (doc.get(alert.value_changed) == db_value) or (
                not db_value and not doc.get(alert.value_changed)
            ):
                return  # value not changed

        if event != "Value Change" and not doc.is_new():
            # reload the doc for the latest values & comments,
            # except for validate type event.
            doc = frappe.get_doc(doc.doctype, doc.name)
        alert.send(doc)
    except TemplateError:
        frappe.throw(
            _(
                "Error while evaluating Notification {0}. Please fix your template."
            ).format(alert)
        )
    except Exception as e:
        error_log = frappe.log_error(message=frappe.get_traceback(), title=str(e))
        frappe.throw(
            _(
                "Error in Notification: {}".format(
                    frappe.utils.get_link_to_form("Error Log", error_log.name)
                )
            )
        )


def get_context(doc):
    return {"doc": doc, "nowdate": nowdate, "frappe.utils": frappe.utils}


def get_doc_fields(doctype_name):
    fields = frappe.get_meta(doctype_name).fields
    filed_list = []
    field_names = ["Customer", "Supplier", "Student", "Employee", "User"]
    for d in fields:
        if d.fieldtype == "Link" and d.options in field_names:
            field = {
                "label": d.label,
                "fieldname": d.fieldname,
                "fieldtype": d.fieldtype,
                "field_options": d.options,
                "doctype_name": doctype_name,
            }
            filed_list.append(field)
        elif d.fieldtype == "Link" and d.options == "DocType":
            fieldname = ""
            field_options = d.fieldname
            for f in fields:
                if f.options == d.fieldname and f.fieldtype == "Dynamic Link":
                    fieldname = f.fieldname
                    break
            if fieldname:
                field = {
                    "fieldname": fieldname,
                    "field_get_value": field_options,
                }
            filed_list.append(field)
    return filed_list


def creat_extra_notification_log(doc):
    enl_doc = frappe.new_doc("Extra Notification Log")
    enl_doc.subject = _(doc.doctype) + " " + _(doc.name)
    enl_doc.doctype_name = doc.doctype
    enl_doc.doc_name = doc.name
    enl_doc.status = "Closed"
    enl_doc.type = "Telegram"
    enl_doc.doc_name = doc.name
    enl_doc.message = _(doc.message_notification)
    enl_doc.party_type = doc.party_type
    enl_doc.to_party = doc.to_party
    enl_doc.from_user = doc.from_user

    enl_doc.insert(ignore_permissions=True)
