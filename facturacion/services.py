from decimal import Decimal
from django.db import transaction
from django.utils import timezone

from .xml_generator import generar_xml_basico


from ventas.models import Venta
from .models import (
    SerieComprobante,
    ComprobanteElectronico,
    ComprobanteElectronicoDetalle,
    EventoComprobanteElectronico,
)


TIPO_MAP = {
    "FACTURA": "01",
    "BOLETA": "03",
}


DOC_CLIENTE_MAP = {
    "DNI": "1",
    "RUC": "6",
    "CE": "4",
    "PASAPORTE": "7",
}


def _get_attr(obj, names, default=""):
    for name in names:
        value = getattr(obj, name, None)
        if value not in [None, ""]:
            return value
    return default


def _datos_emisor(sucursal):
    empresa = getattr(sucursal, "farmacia", None)

    if not empresa:
        raise ValueError("La sucursal no tiene una farmacia/empresa asociada.")

    ruc = _get_attr(empresa, ["ruc", "numero_ruc"])
    razon_social = _get_attr(empresa, ["razon_social", "nombre", "nombre_legal"])
    nombre_comercial = _get_attr(empresa, ["nombre_comercial", "nombre"], razon_social)
    direccion = _get_attr(empresa, ["direccion", "domicilio_fiscal"], "")
    ubigeo = _get_attr(empresa, ["ubigeo"], "")

    if not ruc:
        raise ValueError("La empresa emisora no tiene RUC configurado.")

    if not razon_social:
        raise ValueError("La empresa emisora no tiene razón social configurada.")

    return {
        "ruc": ruc,
        "razon_social": razon_social,
        "nombre_comercial": nombre_comercial,
        "direccion": direccion,
        "ubigeo": ubigeo,
    }


def _datos_cliente(cliente):
    if not cliente:
        return {
            "tipo_documento_cliente": "0",
            "numero_documento_cliente": "",
            "nombre_cliente": "CLIENTES VARIOS",
            "direccion_cliente": "",
            "email_cliente": "",
        }

    tipo_documento = getattr(cliente, "tipo_documento", "") or ""
    numero_documento = getattr(cliente, "numero_documento", "") or ""
    nombres = getattr(cliente, "nombres", "") or ""
    apellidos = getattr(cliente, "apellidos", "") or ""
    razon_social = getattr(cliente, "razon_social", "") or ""
    direccion = getattr(cliente, "direccion", "") or ""
    email = getattr(cliente, "email", "") or ""

    nombre_cliente = razon_social or f"{nombres} {apellidos}".strip() or "CLIENTE"

    return {
        "tipo_documento_cliente": DOC_CLIENTE_MAP.get(tipo_documento, "0"),
        "numero_documento_cliente": numero_documento,
        "nombre_cliente": nombre_cliente,
        "direccion_cliente": direccion,
        "email_cliente": email,
    }


def _obtener_serie(sucursal, tipo_comprobante, ambiente="BETA"):
    serie_default = "F001" if tipo_comprobante == "01" else "B001"

    serie, _ = SerieComprobante.objects.get_or_create(
        sucursal=sucursal,
        tipo_comprobante=tipo_comprobante,
        serie=serie_default,
        ambiente=ambiente,
        defaults={
            "correlativo_actual": 0,
            "activo": True,
        },
    )

    if not serie.activo:
        raise ValueError(f"La serie {serie.serie} está inactiva.")

    return serie


@transaction.atomic
def crear_comprobante_desde_venta(venta_id, tipo_comprobante_pos, usuario=None, ambiente="BETA"):
    venta = Venta.objects.select_for_update().get(id=venta_id)
    venta = Venta.objects.select_related(
        "sucursal",
        "sucursal__farmacia",
        "cliente",
        "vendedor",
    ).prefetch_related(
        "detalles__producto"
    ).get(id=venta.id)
    
    if venta.tipo_comprobante in ["BOLETA", "FACTURA"] and not venta.cliente:
        raise ValueError("Para emitir boleta o factura debes seleccionar un cliente.")

    if venta.estado != "COMPLETADA":
        raise ValueError("Solo se puede facturar una venta completada.")

    if hasattr(venta, "comprobante_electronico"):
        return venta.comprobante_electronico, False

    tipo_comprobante = TIPO_MAP.get(tipo_comprobante_pos)

    if not tipo_comprobante:
        raise ValueError("Solo se puede generar comprobante electrónico para BOLETA o FACTURA.")

    cliente_data = _datos_cliente(venta.cliente)

    if tipo_comprobante == "01" and cliente_data["tipo_documento_cliente"] != "6":
        raise ValueError("Para emitir factura, el cliente debe tener RUC.")

    emisor = _datos_emisor(venta.sucursal)
    serie_obj = _obtener_serie(venta.sucursal, tipo_comprobante, ambiente)
    numero = serie_obj.siguiente_numero()

    comprobante = ComprobanteElectronico.objects.create(
        venta=venta,
        serie_comprobante=serie_obj,
        tipo_comprobante=tipo_comprobante,
        serie=serie_obj.serie,
        numero=numero,
        ambiente=ambiente,
        estado="PENDIENTE",
        moneda="PEN",
        fecha_emision=timezone.now(),
        ruc_emisor=emisor["ruc"],
        razon_social_emisor=emisor["razon_social"],
        nombre_comercial_emisor=emisor["nombre_comercial"],
        direccion_emisor=emisor["direccion"],
        ubigeo_emisor=emisor["ubigeo"],
        tipo_documento_cliente=cliente_data["tipo_documento_cliente"],
        numero_documento_cliente=cliente_data["numero_documento_cliente"],
        nombre_cliente=cliente_data["nombre_cliente"],
        direccion_cliente=cliente_data["direccion_cliente"],
        email_cliente=cliente_data["email_cliente"],
        total_gravado=venta.subtotal,
        total_igv=venta.impuestos,
        total_descuentos=venta.monto_descuento,
        total_importe=venta.total_venta,
        creado_por=usuario,
    )

    for detalle in venta.detalles.all():
        valor_venta = detalle.subtotal_linea
        igv = (valor_venta * Decimal("0.18")).quantize(Decimal("0.01"))
        total_linea = valor_venta + igv

        ComprobanteElectronicoDetalle.objects.create(
            comprobante=comprobante,
            detalle_venta=detalle,
            producto_codigo=getattr(detalle.producto, "codigo_barras", "") or "",
            producto_nombre=detalle.producto.nombre,
            unidad_medida="NIU",
            cantidad=detalle.cantidad,
            valor_unitario=detalle.precio_unitario,
            precio_unitario=detalle.precio_unitario * Decimal("1.18"),
            descuento=detalle.monto_descuento_linea,
            valor_venta=valor_venta,
            igv=igv,
            total_linea=total_linea,
            codigo_tipo_afectacion_igv="10",
        )

    venta.numero_comprobante = comprobante.numero_formateado
    venta.estado_facturacion_electronica = "PENDIENTE"
    venta.uuid_comprobante_fe = comprobante.nombre_archivo_sunat
    venta.save(update_fields=[
        "numero_comprobante",
        "estado_facturacion_electronica",
        "uuid_comprobante_fe",
    ])

    EventoComprobanteElectronico.objects.create(
        comprobante=comprobante,
        estado_anterior="",
        estado_nuevo="PENDIENTE",
        descripcion="Comprobante electrónico creado desde POS.",
        creado_por=usuario,
    )

    return comprobante, True

def generar_xml_comprobante(comprobante):
    xml = generar_xml_basico(comprobante)

    comprobante.xml_firmado = xml
    comprobante.estado = "GENERADO"
    comprobante.save(update_fields=["xml_firmado", "estado"])

    return xml