$(document).on('app_ready', function() {
    // waiting for page to load completely
   
        var route = frappe.get_route();

        if (route[0] == "Form") {
            frappe.ui.form.on(route[1], 
               function (frm) {
                    cur_frm.page.add_menu_item(__("Send To Telegram"), function() {
                        var user_name = frappe.user.name;
                        var user_full_name = frappe.session.user_fullname;
                        var reference_doctype = cur_frm.doctype;
                        var reference_name = cur_frm.docname;
                        var dialog = new frappe.ui.Dialog({
                            'fields': [
                                {'fieldname': 'ht', 'fieldtype': 'HTML'},
                                {'label':'Send To','fieldname': 'telegram_user', 'reqd': 1, 'fieldtype': 'Link','options': 'Telegram User Settings'},
                                {'label':'Subject','fieldname': 'subject', 'reqd': 1, 'fieldtype': 'Data','default': cur_frm.doc.name},
                                {'label':'Message','fieldname': 'message', 'reqd': 1, 'fieldtype': 'SmallText'},
                                {'label':'Attach Document Print','fieldname': 'attach_document_print', 'fieldtype': 'Check'},
                               
                            ],
                            'primary_action_label': 'Send',
                            'title':'Send a Telegram Message',

                            primary_action: function(){
                                var values = dialog.get_values();
                                if(values) {
                                    var space = "\n"+"\n";
                                    var the_message = "From : " + user_full_name + space + values.subject + space + values.message;

                                    // send telegram msg
                                    frappe.call({
                                        method: "erpnext_telegram_integration.erpnext_telegram_integration.doctype.telegram_settings.telegram_settings.send_to_telegram",
                                        args: {
                                            telegram_user: values.telegram_user,
                                            message: the_message,
                                            reference_doctype: reference_doctype,
                                            reference_name: reference_name,
                                            attachment: values.attach_document_print,
                                        },
                                        freeze: true,
                                        callback: (r) => {
                                            frappe.msgprint(__("Successfully Sent to: " + values.telegram_user));
                                            dialog.hide();
                                        }
                                    });

                                    // add comment
                                    var comment_message = 'To : ' + values.telegram_user + space + values.message;
                                    frappe.call({
                                        method: "frappe.desk.form.utils.add_comment",
                                        args: {
                                            reference_doctype: reference_doctype,
                                            reference_name: reference_name,
                                            content: comment_message,
                                            comment_by: frappe.session.user_fullname,
                                            comment_email: frappe.session.user
                                        },
                                    });
                                }
                               
                            },
                            no_submit_on_enter: true,
                        });
                        dialog.fields_dict.ht.$wrapper.html(reference_name);
                        dialog.show();
                    });
                })
 

        }
    
});
