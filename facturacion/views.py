import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET

from .models import ComprobanteElectronico
from .services import crear_comprobante_desde_venta
from .services import generar_xml_comprobante



def _json_body(request):
    try:
        return json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return None


def _json_error(message, status=400):
    return JsonResponse({"error": message}, status=status)


def _comprobante_to_json(comprobante):
    return {
        "id": comprobante.id,
        "venta_id": comprobante.venta_id,
        "tipo_comprobante": comprobante.tipo_comprobante,
        "serie": comprobante.serie,
        "numero": comprobante.numero,
        "numero_formateado": comprobante.numero_formateado,
        "estado": comprobante.estado,
        "ambiente": comprobante.ambiente,
        "total_importe": str(comprobante.total_importe),
        "nombre_archivo_sunat": comprobante.nombre_archivo_sunat,
        "sunat_codigo_respuesta": comprobante.sunat_codigo_respuesta,
        "sunat_descripcion": comprobante.sunat_descripcion,
    }


@login_required
@require_POST
def crear_desde_venta_api(request):
    data = _json_body(request)

    if data is None:
        return _json_error("JSON inválido.", 400)

    venta_id = data.get("venta_id")
    tipo_comprobante = data.get("tipo_comprobante")

    if not venta_id:
        return _json_error("Debe enviar venta_id.", 400)

    if tipo_comprobante not in ["BOLETA", "FACTURA"]:
        return _json_error("tipo_comprobante debe ser BOLETA o FACTURA.", 400)

    try:
        comprobante, creado = crear_comprobante_desde_venta(
            venta_id=venta_id,
            tipo_comprobante_pos=tipo_comprobante,
            usuario=request.user,
            ambiente=data.get("ambiente", "BETA"),
        )

        return JsonResponse({
            "created": creado,
            "comprobante": _comprobante_to_json(comprobante),
        }, status=201 if creado else 200)

    except Exception as e:
        return _json_error(str(e), 400)


@login_required
@require_GET
def comprobante_por_venta_api(request, venta_id):
    comprobante = ComprobanteElectronico.objects.filter(
        venta_id=venta_id
    ).first()

    if not comprobante:
        return _json_error("La venta no tiene comprobante electrónico.", 404)

    return JsonResponse(_comprobante_to_json(comprobante))


@login_required
@require_POST
def generar_xml_api(request, comprobante_id):
    try:
        comprobante = ComprobanteElectronico.objects.get(id=comprobante_id)

        xml = generar_xml_comprobante(comprobante)

        return JsonResponse({
            "message": "XML generado correctamente",
            "xml": xml
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)