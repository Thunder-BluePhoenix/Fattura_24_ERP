frappe.ui.form.on('Sales Invoice', {
    refresh: function(frm) {
        // Check if the document is submitted but not yet sent to Fattura24
        if (frm.doc.docstatus === 1 && !frm.doc.fattura24_id) {
            frm.add_custom_button(__('Send to Fattura24'), function() {
                frappe.call({
                    method: 'fattura24_integration.api.fattura24.send_invoice_to_fattura24',
                    args: {
                        doc: frm.doc
                    },
                    freeze: true,
                    freeze_message: __('Sending invoice to Fattura24...'),
                    callback: function(r) {
                        if (!r.exc) {
                            frappe.msgprint(__('Invoice sent to Fattura24 successfully'));
                            frm.reload_doc();
                        }
                    }
                });
            }, __('Fattura24'));
        }
        
        // Add a button to view the Fattura24 document if it has been sent
        if (frm.doc.fattura24_id) {
            frm.add_custom_button(__('View Fattura24 Logs'), function() {
                frappe.set_route('List', 'Fattura24 Log', {reference_name: frm.doc.name});
            }, __('Fattura24'));
        }
    },
    
    setup: function(frm) {
        // Make sure custom fields are added to Sales Invoice
        ensure_fattura24_custom_fields();
    }
});

// Function to add custom fields to Sales Invoice for Fattura24 integration
function ensure_fattura24_custom_fields() {
    // Check if custom fields already exist
    frappe.call({
        method: 'frappe.client.get_list',
        args: {
            doctype: 'Custom Field',
            filters: {
                dt: 'Sales Invoice',
                fieldname: ['in', ['fattura24_id', 'fattura24_number']]
            },
            fields: ['fieldname']
        },
        callback: function(r) {
            let existing_fields = (r.message || []).map(f => f.fieldname);
            let fields_to_add = [];
            
            // Add fattura24_id if not exists
            if (!existing_fields.includes('fattura24_id')) {
                fields_to_add.push({
                    label: 'Fattura24 ID',
                    fieldname: 'fattura24_id',
                    fieldtype: 'Data',
                    insert_after: 'amended_from',
                    read_only: 1,
                    translatable: 0,
                    unique: 0,
                    no_copy: 1
                });
            }
            
            // Add fattura24_number if not exists
            if (!existing_fields.includes('fattura24_number')) {
                fields_to_add.push({
                    label: 'Fattura24 Number',
                    fieldname: 'fattura24_number',
                    fieldtype: 'Data',
                    insert_after: 'fattura24_id',
                    read_only: 1,
                    translatable: 0,
                    unique: 0,
                    no_copy: 1
                });
            }
            
            // Create any missing custom fields
            if (fields_to_add.length > 0) {
                fields_to_add.forEach(field => {
                    frappe.call({
                        method: 'frappe.client.insert',
                        args: {
                            doc: {
                                doctype: 'Custom Field',
                                dt: 'Sales Invoice',
                                label: field.label,
                                fieldname: field.fieldname,
                                fieldtype: field.fieldtype,
                                insert_after: field.insert_after,
                                read_only: field.read_only,
                                translatable: field.translatable,
                                unique: field.unique,
                                no_copy: field.no_copy
                            }
                        }
                    });
                });
            }
        }
    });
}

