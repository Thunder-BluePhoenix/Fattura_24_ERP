// Copyright (c) 2025, Blue Phoenix and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Fattura24 Settings", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on("Fattura24 Settings", {
    default_xml_template: function(frm) {
        default_templates(frm);
    }
 });


 function default_templates(frm) {
    // Set the main template
    frm.set_value("main_template", `<Fattura24>
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
</Fattura24>`);
    
    // Set the payment template
    frm.set_value("payment_template", `<Payment>
    <Date>{% DATA_SCADENZA %}</Date>
    <Amount>{% IMPORTO_SCADENZA %}</Amount>
    <Paid>false</Paid>
</Payment>`);
    
    // Set the row template
    frm.set_value("row_template", `<Row>
    <Code>{% PRODOTTO_SERVIZIO %}</Code>
    <Description><![CDATA[{% DESCRIZIONE_VOCE %}]]></Description>
    <Qty>{% QUANTITA %}</Qty>
    <Um>{% UNITA_DI_MISURA %}</Um>
    <Price>{% PREZZO %}</Price>
    <VatCode>{% CODICE_ALIQUOTA %}</VatCode>
</Row>`);
    
    // Show a message to the user
    frappe.show_alert({
        message: __('Default templates have been applied'),
        indicator: 'green'
    }, 3);
}

