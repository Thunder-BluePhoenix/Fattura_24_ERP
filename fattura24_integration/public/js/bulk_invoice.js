frappe.ui.form.on('Bulk Invoice Log', {
    refresh: function(frm) {
        // Check if the document is submitted but not yet sent to Fattura24
        if (frm.doc.docstatus === 1 && frm.doc.invoices_submitted === 1) {
            frm.add_custom_button(__('Send to Fattura24 Bulkly'), function() {
                frappe.call({
                    method: 'fattura24_integration.fattura24.api.bulk_fattura24.send_invoice_to_fattura24_funnel_triggered',
                    args: {
                        docname: frm.doc.name
                    },
                    freeze: true,
                    freeze_message: __('Sending invoice to Fattura24...'),
                    callback: function(r) {
                        if (!r.exc) {
                            frappe.msgprint(__('Invoice sent to Fattura24 funeel started successfully'));
                            frm.reload_doc();
                        }
                    }
                });
            }, __('Fattura24'));
        }
        
        // Add a button to view the Fattura24 document if it has been sent
    
    }
});