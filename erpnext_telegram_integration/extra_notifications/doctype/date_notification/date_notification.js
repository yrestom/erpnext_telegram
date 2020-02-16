// Copyright (c) 2020, Youssef Restom and contributors
// For license information, please see license.txt

frappe.ui.form.on('Date Notification', {
	
	get_date_fields: function(frm) {
		// var fields = frappe.get_doc("DocType", cur_frm.doc.doctype_name).fields; 
		// frappe.msgprint(fields);
		frappe.call({
			method: 'erpnext_telegram_integration.extra_notifications.doctype.date_notification.date_notification.get_date_fields',
			args: {"doctype_name":cur_frm.doc.doctype_name},
			callback: (r) => {
				// console.log(r.message[0]);
				// var message = r.message;
				// frappe.msgprint(message);
				// cur_frm.set_value("telegram_token", telegram_token);

				frm.clear_table("date_fields");
				r.message.forEach(d => {
					var child = frm.add_child("date_fields");
					frappe.model.set_value(child.doctype, child.name, "label", d.label)
					frappe.model.set_value(child.doctype, child.name, "fieldname", d.fieldname)
					frappe.model.set_value(child.doctype, child.name, "fieldtype", d.fieldtype)
				});
				cur_frm.refresh_field("date_fields");
				
				// console.log(r.message);
			}
		});
	},
	refresh: function(frm) {
		frm.trigger('event');
	},
	event: function(frm) {
		if(frm.doc.enable) {
			frm.add_custom_button(__('Get Alerts for Today'), function() {
				frappe.call({
					method: 'erpnext_telegram_integration.extra_notifications.doctype.date_notification.date_notification.get_documents_for_today',
					// method: 'erpnext_telegram_integration.extra_notifications.doctype.date_notification.date_notification.trigger_daily_alerts',
					args: {
						notification: frm.doc.name
					},
					callback: function(r) {
						if(r.message) {
							frappe.msgprint(r.message);
						} else {
							frappe.msgprint(__('No alerts for today'));
						}
					}
				});
			});
		}
	},
});
