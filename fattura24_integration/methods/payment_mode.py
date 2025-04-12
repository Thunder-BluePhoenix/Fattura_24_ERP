import frappe

def extract_payment_code(doc, method=None):
    """
    Extract payment method code from mode_of_payment_code field 
    and populate it to custom_code_of_payment_method field
    
    This function is designed to run on before_save event
    """
    # Check if the document has the required attributes
    if hasattr(doc, 'mode_of_payment_code') and hasattr(doc, 'custom_code_of_payment_method'):
        # Check if mode_of_payment_code has a value
        if doc.mode_of_payment_code:
            # Extract the code part (e.g., "MP22" from "MP22-Trattenuta su somme già riscosse")
            payment_code = doc.mode_of_payment_code.split('-')[0]
            
            # Set the extracted code to the custom_code_of_payment_method field
            doc.custom_code_of_payment_method = payment_code

