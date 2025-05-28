import frappe
import requests
import xml.etree.ElementTree as ET
from frappe import _
from datetime import datetime
import json
from xml.sax.saxutils import escape
import re
from frappe.utils.jinja import render_template

@frappe.whitelist()
def send_invoice_to_fattura24(doc, method=None):
    """
    Send the Sales Invoice to Fattura24 when submitted
    """
    if isinstance(doc, str):
        doc = json.loads(doc)
        doc = frappe.get_doc("Sales Invoice", doc.get("name"))
    
    # Check if Fattura24 integration is enabled
    settings = frappe.get_doc("Fattura24 Settings")
    if not settings.enabled:
        return
    
    # Check if invoice has already been sent to Fattura24
    if doc.get("fattura24_id"):
        frappe.msgprint(_("This invoice has already been sent to Fattura24"))
        return
    
    try:
        # Generate XML
        xml_data = generate_fattura24_xml(doc, settings)
        
        # Send to Fattura24
        response = send_to_fattura24(xml_data, settings)
        
        # Process response
        process_fattura24_response(doc, response, xml_data)
        
    except Exception as e:
        # Log error
        create_fattura24_log(
            status="Error",
            reference_doctype="Sales Invoice",
            reference_name=doc.name,
            request_data=xml_data if 'xml_data' in locals() else "",
            response_data="",
            error_message=str(e)
        )
        frappe.log_error(f"Fattura24 Integration Error: {str(e)}", "Fattura24 Integration")
        frappe.msgprint(_("Error sending invoice to Fattura24: {0}").format(str(e)), indicator="red", alert=True)

@frappe.whitelist()
def generate_fattura24_xml(doc, settings=None):
    """
    Generate XML for Fattura24 from Sales Invoice
    """
    if not settings:
        settings = frappe.get_doc("Fattura24 Settings")
    
    # Get customer information
    customer = frappe.get_doc("Customer", doc.customer)
    
    # Get customer address
    address = None
    if doc.customer_address:
        address = frappe.get_doc("Address", doc.customer_address)
    
    # Get customer contact
    contact = None
    if doc.contact_person:
        contact = frappe.get_doc("Contact", doc.contact_person)
    
    # Format XML using templates
    xml_data = settings.main_template
    
    # Replace customer details
    xml_data = xml_data.replace("{% RAGIONE_SOCIALE %}", customer.customer_name or "")
    xml_data = xml_data.replace("{% PARTITA_IVA %}", str(customer.custom_vat_code)or "")
    
    # Address details
    if address:
        xml_data = xml_data.replace("{% VIA %}", (address.address_line1 or "") + (f", {address.address_line2}" if address.address_line2 else ""))
        xml_data = xml_data.replace("{% CAP %}", str(address.pincode) or "")
        xml_data = xml_data.replace("{% LOCALITA %}", address.city or "")
        xml_data = xml_data.replace("{% PR %}", address.state or "")
        xml_data = xml_data.replace("{% IT %}", address.country or "")
    else:
        xml_data = xml_data.replace("{% VIA %}", "")
        xml_data = xml_data.replace("{% CAP %}", "")
        xml_data = xml_data.replace("{% LOCALITA %}", "")
        xml_data = xml_data.replace("{% PR %}", "")
        xml_data = xml_data.replace("{% IT %}", "")
    
    # Contact details
    if contact:
        # Get email and phone from contact
        email = ""
        phone = ""
        for email_id in contact.email_ids:
            if email_id.is_primary:
                email = email_id.email_id
                break
        for phone_no in contact.phone_nos:
            if phone_no.is_primary_phone:
                phone = phone_no.phone
                break
            
        xml_data = xml_data.replace("{% EMAIL %}", email or "")
        xml_data = xml_data.replace("{% TELEFONO %}", str(phone) or "")
        
    else:
        xml_data = xml_data.replace("{% EMAIL %}", "")
        xml_data = xml_data.replace("{% TELEFONO %}", "")

    if customer.custom_pec:
        xml_data = xml_data.replace("{% PEC %}", str(customer.custom_pec))
    else:
        xml_data = xml_data.replace("{% PEC %}", "")


    if doc.custom_note:
        xml_data = xml_data.replace("{% NOTA_PIEDE %}", str(customer.custom_note))
    else:
        xml_data = xml_data.replace("{% NOTA_PIEDE %}", "")
    xml_data = xml_data.replace("{% CODICE_SDI %}", str(customer.custom_destination_code) or "0000000")
    
    # Invoice details
    xml_data = xml_data.replace("{% OGGETTO %}", doc.custom_object or f"Invoice {doc.name}")
    xml_data = xml_data.replace("{% TOTALE_IMPONIBILE %}", str(doc.custom_grand_total_cost))
    xml_data = xml_data.replace("{% TOTALE_IVA %}", str(doc.total_taxes_and_charges))
    xml_data = xml_data.replace("{% TOTALE_FATTURA %}", str(doc.grand_total))
    
    # Payment details
    xml_data = xml_data.replace("{% CODICE_PAGAMENTO %}", doc.get("custom_payment_code_") or "MP05")  # Default to bank transfer
    xml_data = xml_data.replace("{% DENOMINAZIONE_BANCA %}", settings.default_bank_name or "")
    xml_data = xml_data.replace("{% IBAN %}", settings.default_iban or "")
    
    # Generate payment rows
    payment_rows = ""
    if doc.payment_schedule:
        for payment in doc.payment_schedule:
            payment_xml = settings.payment_template
            payment_xml = payment_xml.replace("{% DATA_SCADENZA %}", payment.due_date.strftime("%Y-%m-%d"))
            payment_xml = payment_xml.replace("{% IMPORTO_SCADENZA %}", str(payment.payment_amount))
            payment_rows += payment_xml + "\n"
    
    xml_data = xml_data.replace("{% ELENCO_SCADENZE %}", payment_rows)



    fatt_des_doc = frappe.get_doc("Template and Print format Settings")
    if doc.custom_peneus_hub == 1 and doc.custom_tyre_hotel == 0:
        fatt_des = fatt_des_doc.fattura_description
        description = render_template(fatt_des, {"doc": doc})
    elif doc.custom_tyre_hotel == 1 and doc.custom_peneus_hub == 0:
        fatt_des = fatt_des_doc.fattura_description_th
        description = render_template(fatt_des, {"doc": doc})
    
    # Generate item rows
    item_rows = ""
    # for item in doc.items:
    row_xml = settings.row_template
    row_xml = row_xml.replace("{% PRODOTTO_SERVIZIO %}", doc.name or "")
    row_xml = row_xml.replace("{% DESCRIZIONE_VOCE %}", description or "")
    row_xml = row_xml.replace("{% QUANTITA %}", "1")
    row_xml = row_xml.replace("{% UNITA_DI_MISURA %}", "pz")
    row_xml = row_xml.replace("{% PREZZO %}", str(doc.custom_grand_total_cost))
    
    # Get tax rate from tax template
    tax_rate = "22"  # Default to 22%
    if doc.taxes_and_charges:
        tax_template = frappe.get_doc("Sales Taxes and Charges Template", doc.taxes_and_charges)
        for tax in tax_template.taxes:
            tax_rate = str(int(tax.rate))
            break
    
    row_xml = row_xml.replace("{% CODICE_ALIQUOTA %}", tax_rate)
    item_rows += row_xml + "\n"
    
    xml_data = xml_data.replace("{% ELENCO_RIGHE %}", item_rows)
    
    return xml_data

def send_to_fattura24(xml_data, settings=None):
    """
    Send XML data to Fattura24
    """
    if not settings:
        settings = frappe.get_doc("Fattura24 Settings")
    
    url = f"{settings.api_url}/SaveDocument"
    
    # Prepare the data to be sent
    data = {
        'apiKey': settings.get_password('api_key'),
        'xml': xml_data
    }
    
    # Send request to Fattura24
    response = requests.post(url, data=data)
    
    # Check if request was successful
    if response.status_code != 200:
        frappe.throw(_("Error connecting to Fattura24 API: {0}").format(response.text))
    
    return response.text

def process_fattura24_response(doc, response_text, request_data):
    """
    Process response from Fattura24
    """
    try:
        # Parse XML response
        root = ET.fromstring(response_text)
        
        # Check if operation was successful
        return_code = root.find('returnCode')
        if return_code is not None and return_code.text == '0':
            # Get Fattura24 document ID and number
            doc_id = root.find('docId').text if root.find('docId') is not None else ""
            doc_number = root.find('docNumber').text if root.find('docNumber') is not None else ""
            
            # Update Sales Invoice with Fattura24 information
            doc.db_set('fattura24_id', doc_id)
            doc.db_set('fattura24_number', doc_number)
            
            # Create success log
            create_fattura24_log(
                status="Success",
                reference_doctype="Sales Invoice",
                reference_name=doc.name,
                fattura24_id=doc_id,
                fattura24_number=doc_number,
                request_data=request_data,
                response_data=response_text
            )
            
            frappe.msgprint(_("Invoice successfully sent to Fattura24. Document ID: {0}").format(doc_id))
        else:
            # Extract error description
            description = root.find('description').text if root.find('description') is not None else "Unknown error"
            
            # Create error log
            create_fattura24_log(
                status="Error",
                reference_doctype="Sales Invoice",
                reference_name=doc.name,
                request_data=request_data,
                response_data=response_text,
                error_message=description
            )
            
            frappe.throw(_("Error from Fattura24: {0}").format(description))
    
    except ET.ParseError:
        frappe.throw(_("Invalid response from Fattura24: {0}").format(response_text))

def create_fattura24_log(status, reference_doctype, reference_name, request_data="", response_data="", error_message="", fattura24_id="", fattura24_number=""):
    """
    Create a log entry for Fattura24 integration
    """
    log = frappe.new_doc("Fattura24 Log")
    log.status = status
    log.reference_doctype = reference_doctype
    log.reference_name = reference_name
    log.creation_date = datetime.now()
    log.request_data = request_data
    log.response_data = response_data
    log.error_message = error_message
    log.fattura24_id = fattura24_id
    log.fattura24_number = fattura24_number
    
    log.save(ignore_permissions=True)
    frappe.db.commit()
    
    return log

