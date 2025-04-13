import frappe
from frappe.model.document import Document

class Fattura24Settings(Document):
    def validate(self):
        # Set default XML templates if not present
        if not self.main_template:
            self.main_template = self.get_default_main_template()
        
        if not self.payment_template:
            self.payment_template = self.get_default_payment_template()
        
        if not self.row_template:
            self.row_template = self.get_default_row_template()

    def get_default_main_template(self):
        """Return the default XML template for Fattura24"""
        return """<Fattura24>
    <Document>
        <DocumentType>FE</DocumentType>
        <CustomerName><![CDATA[{% RAGIONE_SOCIALE %}]]></CustomerName>
        <CustomerAddress><![CDATA[{% VIA %}]]></CustomerAddress>
        <CustomerPostcode>{% CAP %}</CustomerPostcode>
        <CustomerCity>{% LOCALITA %}</CustomerCity>
        <CustomerProvince>{% PR %}</CustomerProvince>
        <CustomerCountry>IT</CustomerCountry>
        <CustomerFiscalCode/>
        <CustomerVatCode>{% PARTITA_IVA %}</CustomerVatCode>
        <CustomerCellPhone>{% TELEFONO %}</CustomerCellPhone>
        <CustomerEmail>{% EMAIL %}</CustomerEmail>
        <Object><![CDATA[{% OGGETTO %}]]></Object>
        <FeCustomerPec>{% PEC %}</FeCustomerPec>
        <FeDestinationCode>{% CODICE_SDI %}</FeDestinationCode>
        <FePaymentCode>{% CODICE_PAGAMENTO %}</FePaymentCode>
        <PaymentMethodName>{% DENOMINAZIONE_BANCA %}</PaymentMethodName>
        <PaymentMethodDescription>{% IBAN %}</PaymentMethodDescription>
        <TotalWithoutTax>{% TOTALE_IMPONIBILE %}</TotalWithoutTax>
        <VatAmount>{% TOTALE_IVA %}</VatAmount>
        <Total>{% TOTALE_FATTURA %}</Total>
        <FootNotes><![CDATA[{% NOTA_PIEDE %}]]></FootNotes>
        <SendEmail>false</SendEmail>
        <UpdateStorage>0</UpdateStorage>
        <Payments>
{% ELENCO_SCADENZE %}
        </Payments>
        <Rows>
{% ELENCO_RIGHE %}
        </Rows>
    </Document>
</Fattura24>"""

    def get_default_payment_template(self):
        """Return the default payment XML template for Fattura24"""
        return """<Payment>
    <Date>{% DATA_SCADENZA %}</Date>
    <Amount>{% IMPORTO_SCADENZA %}</Amount>
    <Paid>false</Paid>
</Payment>"""

    def get_default_row_template(self):
        """Return the default row XML template for Fattura24"""
        return """<Row>
    <Code>{% PRODOTTO_SERVIZIO %}</Code>
    <Description><![CDATA[{% DESCRIZIONE_VOCE %}]]></Description>
    <Qty>{% QUANTITA %}</Qty>
    <Um>{% UNITA_DI_MISURA %}</Um>
    <Price>{% PREZZO %}</Price>
    <VatCode>{% CODICE_ALIQUOTA %}</VatCode>
</Row>"""

