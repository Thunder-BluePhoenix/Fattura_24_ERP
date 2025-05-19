import frappe
from frappe import _
from frappe.utils import getdate

def before_save(doc, method):
    populate_custom_object(doc, method)



def populate_custom_object(doc, method):
    # 1. Get month number from custom_start_date_for_storage_cost_
    if not doc.custom_start_date_for_storage_cost_:
        return  # Skip if date is not provided

    # Ensure it's a date object
    start_date = getdate(doc.custom_start_date_for_storage_cost_)
    month_number = start_date.strftime("%m")  # Two-digit month

    # 2. Determine service name
    service = None
    if doc.custom_peneus_hub:
        service = "PneusHub"
    elif doc.custom_tyre_hotel:
        service = "TyreHotel"

    if not service:
        return  # Skip if neither service is selected

    # 3. Get the customer name and create slug
    if not doc.customer:
        return  # Skip if no customer

    customer_doc = frappe.get_doc("Customer", doc.customer)
    name_parts = customer_doc.customer_name.strip().split()
    customer_slug = ''.join(part.capitalize() for part in name_parts)

    # 4. Combine into final format: (monthnumber).(service).(customer slug)
    doc.custom_object = f"{month_number}.{service}.{customer_slug}"

    if month_number == "01":
        doc.custom_month = "Gennaio"
    elif month_number == "02":
        doc.custom_month = "Febbraio"
    elif month_number == "03":
        doc.custom_month = "Marzo"
    elif month_number == "04":
        doc.custom_month = "Aprile"
    elif month_number == "05":
        doc.custom_month = "Maggio"
    elif month_number == "06":
        doc.custom_month = "Giugno"
    elif month_number == "07":
        doc.custom_month = "Luglio"
    elif month_number == "08":
        doc.custom_month = "Agosto"
    elif month_number == "09":
        doc.custom_month = "Settembre"
    elif month_number == "10":
        doc.custom_month = "Ottobre"
    elif month_number == "11":
        doc.custom_month = "Novembre"
    elif month_number == "12":
        doc.custom_month = "Dicembre"


 
    
# $mesi["01"]="Gennaio";
# $mesi["02"]="Febbraio";
# $mesi["03"]="Marzo";
# $mesi["04"]="Aprile";
# $mesi["05"]="Maggio";
# $mesi["06"]="Giugno";
# $mesi["07"]="Luglio";
# $mesi["08"]="Agosto";
# $mesi["09"]="Settembre";
# $mesi["10"]="Ottobre";
# $mesi["11"]="Novembre";
# $mesi["12"]="Dicembre";




