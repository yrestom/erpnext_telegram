$(document).on('app_ready', function() {
    // waiting for page to load completely
   
        var route = frappe.get_route();

        if (route[0] == "Form") {
            frappe.ui.form.on(route[1], {
                refresh: function (frm) {
                    console.log("doctype =" + frm.doctype);
                    cur_frm.page.add_menu_item(__("Send To Telegram"), function() {
                        // frappe.msgprint("Send To Telegram");
                        var user_name = frappe.user.name;
                        var user_full_name = frappe.session.user_fullname;
                        var reference_doctype = cur_frm.doctype;
                        var reference_name = cur_frm.docname;
                        var dialog = new frappe.ui.Dialog({
                            'fields': [
                                {'fieldname': 'ht', 'fieldtype': 'HTML'},
                                // {'label':'Sender','fieldname': 'sender', 'reqd': 1, 'fieldtype': 'Data','default': user_full_name},
                                {'label':'Send To','fieldname': 'telegram_user', 'reqd': 1, 'fieldtype': 'Link','options': 'Telegram User Settings'},
                                {'label':'Subject','fieldname': 'subject', 'reqd': 1, 'fieldtype': 'Data','default': cur_frm.doc.name},
                                {'label':'Message','fieldname': 'message', 'reqd': 1, 'fieldtype': 'SmallText'},
                                {'label':'Attach Document Print','fieldname': 'attach_document_print', 'fieldtype': 'Check'},
                                {'label':'Select Print Format','fieldname': 'select_print_format', 'fieldtype': 'Select'},
                                {'label':'Select Languages','fieldname': 'language_sel', 'fieldtype': 'Select'},

                            ],
                            'primary_action_label': 'Send',
                            'title':'Send a Telegram Message',

                            // setup_print: function() {
                            //     // print formats
                            //     var fields = this.dialog.fields_dict;
                        
                            //     // toggle print format
                            //     $(fields.attach_document_print.input).click(function() {
                            //         $(fields.select_print_format.wrapper).toggle($(this).prop("checked"));
                            //     });
                        
                            //     // select print format
                            //     $(fields.select_print_format.wrapper).toggle(false);
                        
                            //     if (cur_frm) {
                            //         $(fields.select_print_format.input)
                            //             .empty()
                            //             .add_options(cur_frm.print_preview.print_formats)
                            //             .val(cur_frm.print_preview.print_formats[0]);
                            //     } else {
                            //         $(fields.attach_document_print.wrapper).toggle(false);
                            //     }
                        
                            // },

                            // selected_format: function() {
                            //     return this.dialog.fields_dict.select_print_format.input.value || (this.frm && this.frm.meta.default_print_format) || "Standard";
                            // },
                        
                            // get_print_format: function(format) {
                            //     if (!format) {
                            //         format = this.selected_format();
                            //     }
                        
                            //     if (locals["Print Format"] && locals["Print Format"][format]) {
                            //         return locals["Print Format"][format];
                            //     } else {
                            //         return {};
                            //     }
                            // },


                            
                            primary_action: function(){
                                var values = dialog.get_values();
                                if(values) {
                                    var space = "\n"+"\n";
                                    var the_message = "From : " + user_full_name + space + values.subject + space + values.message;
                                    frappe.call({
                                        method: "erpnext_telegram_integration.erpnext_telegram_integration.doctype.telegram_settings.telegram_settings.send_to_telegram",
                                        args: {
                                            telegram_user: values.telegram_user,
                                            message: the_message,
                                            reference_doctype: reference_doctype,
                                            reference_name: reference_name,
                                        },
                                        freeze: true,
                                        callback: (r) => {
                                            frappe.msgprint(__("Successfully Sent to: " + values.telegram_user));
                                            dialog.hide();
                                        }
                                    });
                                }
                                // frappe.show_alert(d.get_values());
                                // frappe.msgprint(d.get_values());
                                
                                // frappe.msgprint(values.telegram_user);
                                // frappe.msgprint(values.message);
                                // dialog.hide();
                            },
                            no_submit_on_enter: true,
                        });
                        dialog.fields_dict.ht.$wrapper.html(reference_name);
                        dialog.show();
                    });
                }
            })
 

        }
    
});