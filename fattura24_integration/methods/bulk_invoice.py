import frappe


def count_pending_invoices(doc, method = None):
    count = 0
    for invoice in doc.customer_details:
        if invoice.sent_to_fattura24 != 1 and invoice.invoice_id is not None:
            count += 1

    doc.invoices_to_be_sent_to_fattura24 = count