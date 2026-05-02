# traslados/views.py

import json

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_GET, require_POST, require_http_methods

from core.models import Sucursal
from inventario.models import Producto, StockProducto
from .models import Transferencia, DetalleTransferencia


def _json_body(request):
    try:
        return json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return None


def _json_error(message, status=400):
    return JsonResponse({"error": message}, status=status)


def _transferencia_to_json(transferencia, incluir_detalles=False):
    data = {
        "id": transferencia.id,
        "sucursal_origen": transferencia.sucursal_origen_id,
        "sucursal_origen_nombre": str(transferencia.sucursal_origen),
        "sucursal_destino": transferencia.sucursal_destino_id,
        "sucursal_destino_nombre": str(transferencia.sucursal_destino),
        "estado": transferencia.estado,
        "observaciones": transferencia.observaciones or "",
        "solicitado_por": str(transferencia.solicitado_por),
        "fecha_creacion": transferencia.fecha_creacion.isoformat(),
        "fecha_envio": transferencia.fecha_envio.isoformat() if transferencia.fecha_envio else None,
        "fecha_recepcion": transferencia.fecha_recepcion.isoformat() if transferencia.fecha_recepcion else None,
    }

    if incluir_detalles:
        data["detalles"] = [
            {
                "id": detalle.id,
                "producto": detalle.producto_id,
                "producto_nombre": detalle.producto.nombre,
                "stock_origen": detalle.stock_origen_id,
                "lote": detalle.stock_origen.lote,
                "cantidad": detalle.cantidad,
                "stock_disponible": detalle.stock_origen.cantidad,
            }
            for detalle in transferencia.detalles.select_related(
                "producto",
                "stock_origen"
            ).all()
        ]

    return data


@login_required
def traslados_home_view(request):
    transferencias = Transferencia.objects.select_related(
        "sucursal_origen",
        "sucursal_destino",
        "solicitado_por",
    ).order_by("-fecha_creacion")

    return render(request, "traslados_templates/traslados_home.html", {
        "transferencias": transferencias,
    })


@login_required
def traslado_create_view(request):
    sucursales = Sucursal.objects.all().order_by("nombre")
    productos = Producto.objects.all().order_by("nombre")

    return render(request, "traslados_templates/traslado_form.html", {
        "sucursales": sucursales,
        "productos": productos,
        "modo": "crear",
    })


@login_required
def traslado_edit_view(request, transferencia_id):
    transferencia = get_object_or_404(
        Transferencia.objects.select_related(
            "sucursal_origen",
            "sucursal_destino",
            "solicitado_por"
        ),
        id=transferencia_id
    )

    if transferencia.estado != "PENDIENTE":
        return render(request, "traslados_templates/traslado_form.html", {
            "error": "Solo puedes editar traslados en estado PENDIENTE.",
            "transferencia": transferencia,
            "modo": "editar",
        })

    sucursales = Sucursal.objects.all().order_by("nombre")
    productos = Producto.objects.all().order_by("nombre")

    return render(request, "traslados_templates/traslado_form.html", {
        "sucursales": sucursales,
        "productos": productos,
        "transferencia": transferencia,
        "modo": "editar",
    })


@login_required
@require_GET
def transferencias_list_api(request):
    transferencias = Transferencia.objects.select_related(
        "sucursal_origen",
        "sucursal_destino",
        "solicitado_por",
    ).order_by("-fecha_creacion")

    data = [_transferencia_to_json(t) for t in transferencias]

    return JsonResponse({
        "count": len(data),
        "results": data,
    })


@login_required
@require_GET
def transferencia_detail_api(request, transferencia_id):
    transferencia = get_object_or_404(
        Transferencia.objects.select_related(
            "sucursal_origen",
            "sucursal_destino",
            "solicitado_por",
        ).prefetch_related("detalles__producto", "detalles__stock_origen"),
        id=transferencia_id
    )

    return JsonResponse(_transferencia_to_json(transferencia, incluir_detalles=True))


@login_required
@require_POST
@transaction.atomic
def transferencia_create_api(request):
    data = _json_body(request)

    if data is None:
        return _json_error("JSON inválido.", 400)

    sucursal_origen_id = data.get("sucursal_origen")
    sucursal_destino_id = data.get("sucursal_destino")
    observaciones = data.get("observaciones", "")
    detalles = data.get("detalles", [])

    if not sucursal_origen_id or not sucursal_destino_id:
        return _json_error("Debes seleccionar sucursal de origen y destino.", 400)

    if str(sucursal_origen_id) == str(sucursal_destino_id):
        return _json_error("La sucursal de origen y destino no pueden ser la misma.", 400)

    if not detalles:
        return _json_error("Debes agregar al menos un producto al traslado.", 400)

    transferencia = Transferencia.objects.create(
        sucursal_origen_id=sucursal_origen_id,
        sucursal_destino_id=sucursal_destino_id,
        solicitado_por=request.user,
        observaciones=observaciones,
        estado="PENDIENTE",
    )

    for item in detalles:
        producto_id = item.get("producto")
        stock_origen_id = item.get("stock_origen")
        cantidad = int(item.get("cantidad") or 0)

        if cantidad <= 0:
            return _json_error("La cantidad debe ser mayor a cero.", 400)

        stock = StockProducto.objects.select_related("producto", "sucursal").filter(
            id=stock_origen_id,
            producto_id=producto_id,
            sucursal_id=sucursal_origen_id,
        ).first()

        if not stock:
            return _json_error("El lote seleccionado no pertenece al producto o sucursal de origen.", 400)

        if stock.cantidad < cantidad:
            return _json_error(f"Stock insuficiente para {stock.producto.nombre}.", 400)

        DetalleTransferencia.objects.create(
            transferencia=transferencia,
            producto_id=producto_id,
            stock_origen=stock,
            cantidad=cantidad,
        )

    return JsonResponse({
        "message": "Traslado creado correctamente.",
        "transferencia": _transferencia_to_json(transferencia, incluir_detalles=True),
    }, status=201)


@login_required
@require_http_methods(["PUT", "PATCH"])
@transaction.atomic
def transferencia_update_api(request, transferencia_id):
    transferencia = get_object_or_404(Transferencia, id=transferencia_id)

    if transferencia.estado != "PENDIENTE":
        return _json_error("Solo puedes editar traslados en estado PENDIENTE.", 400)

    data = _json_body(request)

    if data is None:
        return _json_error("JSON inválido.", 400)

    sucursal_origen_id = data.get("sucursal_origen")
    sucursal_destino_id = data.get("sucursal_destino")
    observaciones = data.get("observaciones", "")
    detalles = data.get("detalles", [])

    if not sucursal_origen_id or not sucursal_destino_id:
        return _json_error("Debes seleccionar sucursal de origen y destino.", 400)

    if str(sucursal_origen_id) == str(sucursal_destino_id):
        return _json_error("La sucursal de origen y destino no pueden ser la misma.", 400)

    if not detalles:
        return _json_error("Debes agregar al menos un producto al traslado.", 400)

    transferencia.sucursal_origen_id = sucursal_origen_id
    transferencia.sucursal_destino_id = sucursal_destino_id
    transferencia.observaciones = observaciones
    transferencia.save()

    transferencia.detalles.all().delete()

    for item in detalles:
        producto_id = item.get("producto")
        stock_origen_id = item.get("stock_origen")
        cantidad = int(item.get("cantidad") or 0)

        if cantidad <= 0:
            return _json_error("La cantidad debe ser mayor a cero.", 400)

        stock = StockProducto.objects.select_related("producto", "sucursal").filter(
            id=stock_origen_id,
            producto_id=producto_id,
            sucursal_id=sucursal_origen_id,
        ).first()

        if not stock:
            return _json_error("El lote seleccionado no pertenece al producto o sucursal de origen.", 400)

        if stock.cantidad < cantidad:
            return _json_error(f"Stock insuficiente para {stock.producto.nombre}.", 400)

        DetalleTransferencia.objects.create(
            transferencia=transferencia,
            producto_id=producto_id,
            stock_origen=stock,
            cantidad=cantidad,
        )

    return JsonResponse({
        "message": "Traslado actualizado correctamente.",
        "transferencia": _transferencia_to_json(transferencia, incluir_detalles=True),
    })


@login_required
@require_POST
@transaction.atomic
def transferencia_delete_api(request, transferencia_id):
    transferencia = get_object_or_404(Transferencia, id=transferencia_id)

    if transferencia.estado != "PENDIENTE":
        return _json_error("Solo puedes eliminar traslados en estado PENDIENTE.", 400)

    transferencia.delete()

    return JsonResponse({
        "message": "Traslado eliminado correctamente."
    })


@login_required
@require_POST
def transferencia_enviar_api(request, transferencia_id):
    transferencia = get_object_or_404(Transferencia, id=transferencia_id)

    try:
        transferencia.marcar_como_enviada(request.user)
        return JsonResponse({"status": "Traslado enviado correctamente."})
    except ValidationError as e:
        return _json_error(str(e), 400)


@login_required
@require_POST
def transferencia_recibir_api(request, transferencia_id):
    transferencia = get_object_or_404(Transferencia, id=transferencia_id)

    try:
        transferencia.marcar_como_recibida(request.user)
        return JsonResponse({"status": "Traslado recibido correctamente."})
    except ValidationError as e:
        return _json_error(str(e), 400)
    
    
