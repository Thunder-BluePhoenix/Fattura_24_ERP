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



