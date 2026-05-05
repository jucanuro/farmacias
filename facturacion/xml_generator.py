from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom


def prettify_xml(elem):
    rough = tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough)
    return reparsed.toprettyxml(indent="  ")


def generar_xml_basico(comprobante):
    root = Element("Invoice")

    SubElement(root, "ID").text = comprobante.numero_formateado
    SubElement(root, "IssueDate").text = comprobante.fecha_emision.strftime("%Y-%m-%d")

    SubElement(root, "DocumentCurrencyCode").text = comprobante.moneda

    # Emisor
    supplier = SubElement(root, "AccountingSupplierParty")
    SubElement(supplier, "CustomerAssignedAccountID").text = comprobante.ruc_emisor
    SubElement(supplier, "PartyName").text = comprobante.razon_social_emisor

    # Cliente
    customer = SubElement(root, "AccountingCustomerParty")
    SubElement(customer, "CustomerAssignedAccountID").text = comprobante.numero_documento_cliente or "-"
    SubElement(customer, "PartyName").text = comprobante.nombre_cliente

    # Totales
    SubElement(root, "LegalMonetaryTotal").text = str(comprobante.total_importe)

    # Detalles
    for item in comprobante.detalles.all():
        line = SubElement(root, "InvoiceLine")

        SubElement(line, "ID").text = str(item.id)
        SubElement(line, "InvoicedQuantity").text = str(item.cantidad)
        SubElement(line, "LineExtensionAmount").text = str(item.valor_venta)

        SubElement(line, "ItemName").text = item.producto_nombre

    return prettify_xml(root)