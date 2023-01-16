// Copyright (c) 2019, Youssef Restom and contributors
// For license information, please see license.txt

frappe.ui.form.on('Telegram User Settings', {
	// refresh: function(frm) {
	// set_field_options("party", ["User","Employee","Customer", "Supplier", "Contact"]);
	// },

	setup: function (frm) {
		frm.set_query("party", function () {
			var doctypes = ["User", "Employee", "Customer", "Supplier", "Contact"];
			return {
				filters: { "name": ["in", doctypes] }
			};
		});
	},


	generate_telegram_token: function (frm) {
		frappe.call({
			method: 'erpnext_telegram_integration.erpnext_telegram_integration.doctype.telegram_user_settings.telegram_user_settings.generate_telegram_token',
			args: { "is_group_chat": cur_frm.doc.is_group_chat },
			callback: (r) => {
				// console.log(r.message[0]);
				var telegram_token = r.message;

				cur_frm.set_value("telegram_token", telegram_token);
				frappe.model.get_value('Telegram Settings', { name: frm.doc.telegram_settings }, 'bot_name', (r) => {
					if (r.bot_name) {
						navigator.clipboard.writeText(frm.doc.telegram_token).then(() => {
							frappe.show_alert({ message: __('Telegram Token copied to your clipboard!'), indicator: 'green' }, 20);
							window.open(`https://t.me/${r.bot_name}`, '_blank');
						});
					}

				});

			}
		});
	},

	get_chat_id: function (frm) {
		frappe.call({
			method: 'erpnext_telegram_integration.erpnext_telegram_integration.doctype.telegram_user_settings.telegram_user_settings.get_chat_id_button',
			args: { "telegram_token": frm.doc.telegram_token.toString(), "telegram_settings": frm.doc.telegram_settings },
			callback: (r) => {
				frm.set_value("telegram_chat_id", r.message);
				refresh_field("telegram_chat_id");
			}
		});
	}
});
