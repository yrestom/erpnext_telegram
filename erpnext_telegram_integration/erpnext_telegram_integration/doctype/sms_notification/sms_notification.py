# -*- coding: utf-8 -*-
# Copyright (c) 2019, Youssef Restom and contributors
# For license information, please see license.txt
from __future__ import unicode_literals
import frappe
import json, os
from frappe import _
from frappe.model.document import Document
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
from frappe.core.doctype.sms_settings.sms_settings import send_sms
from frappe.contacts.doctype.contact.contact import (
    get_default_contact,
    get_contact_details,
)


class SMSNotification(Document):
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
        if not validate_sms_settings():
            frappe.msgprint(_("Please setup SMS Settings"))

        if self.event in ("Days Before", "Days After") and not self.date_changed:
            frappe.throw(_("Please specify which date field must be checked"))

        if self.event == "Value Change" and not self.value_changed:
            frappe.throw(_("Please specify which value field must be checked"))

        self.validate_forbidden_types()
        self.validate_condition()
        self.validate_standard()
        frappe.cache().hdel("sms_notifications", self.document_type)

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

        if self.channel == "SMS":
            self.send_sms_msg(doc, context)

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

    def send_sms_msg(self, doc, context):
        space = "\n"
        message = frappe.render_template(self.subject, context) + space
        message = message + frappe.render_template(self.message, context)
        recipients_no_list = self.get_recipients_no_list()
        recipients_no_list.extend(self.get_dynamic_recipients(doc))
        if validate_sms_settings():
            send_sms(
                receiver_list=recipients_no_list,
                msg=message,
            )

    def get_dynamic_recipients(self, doc):
        recipients_no_list = []
        field_names = ["Customer", "Supplier", "Student", "Employee"]
        if self.dynamic_recipients:
            fields = get_doc_fields(self.document_type)
            for d in fields:
                if doc.get(d["fieldname"]):
                    party = d.get("field_options")
                    if not party:
                        if (
                            d.get("field_get_value")
                            and doc.get(d["field_get_value"]) in field_names
                        ):
                            party = doc.get(d["field_get_value"])
                        else:
                            break
                    default_contact = get_default_contact(
                        party, doc.get(d["fieldname"])
                    )
                    contact_details = get_contact_details(default_contact)
                    if contact_details.get("contact_mobile"):
                        recipients_no_list.append(contact_details.get("contact_mobile"))

        return recipients_no_list

    def get_recipients_no_list(self):
        if not self.recipients:
            return []
        recipients_no_list = []
        for contact in self.recipients:
            if contact.mobile_no:
                recipients_no_list.append(contact.mobile_no)
        return recipients_no_list

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
def run_sms_notifications(doc, method):
    """Run notifications for this method"""
    if frappe.flags.in_import or frappe.flags.in_patch or frappe.flags.in_install:
        return

    if doc.flags.sms_notifications_executed == None:
        doc.flags.sms_notifications_executed = []

    if doc.flags.sms_notifications == None:
        alerts = frappe.cache().hget("sms_notifications", doc.doctype)
        if alerts == None:
            alerts = frappe.get_all(
                "SMS Notification",
                fields=["name", "event", "method"],
                filters={"enabled": 1, "document_type": doc.doctype},
            )
            frappe.cache().hset("sms_notifications", doc.doctype, alerts)
        doc.flags.sms_notifications = alerts

    if not doc.flags.sms_notifications:
        return

    def _evaluate_alert(alert):
        if not alert.name in doc.flags.sms_notifications_executed:
            evaluate_alert(doc, alert.name, alert.event)
            doc.flags.sms_notifications_executed.append(alert.name)

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

    for alert in doc.flags.sms_notifications:
        event = event_map.get(method, None)
        if event and alert.event == event:
            _evaluate_alert(alert)
        elif alert.event == "Method" and method == alert.method:
            _evaluate_alert(alert)


@frappe.whitelist()
def get_documents_for_today(notification):
    notification = frappe.get_doc("SMS Notification", notification)
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
            "SMS Notification",
            filters={"event": ("in", ("Days Before", "Days After")), "enabled": 1},
        )
        for d in doc_list:
            alert = frappe.get_doc("SMS Notification", d.name)

            for doc in alert.get_documents_for_today():
                evaluate_alert(doc, alert, alert.event)
                frappe.db.commit()


def evaluate_alert(doc, alert, event):
    from jinja2 import TemplateError

    try:
        if isinstance(alert, string_types):
            alert = frappe.get_doc("SMS Notification", alert)

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
    field_names = ["Customer", "Supplier", "Student", "Employee"]
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


def validate_sms_settings():
    sms_setting = frappe.get_single("SMS Settings")
    if sms_setting.sms_gateway_url:
        return True
    else:
        return False
