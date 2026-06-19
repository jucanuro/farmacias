# traslados/views.py

import json

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST, require_http_methods

from core.models import Sucursal
from inventario.models import Producto, StockProducto, MovimientoInventario
from .models import TrasladoStock, DetalleTrasladoStock


def _json_body(request):
    try:
        return json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return None


def _json_error(message, status=400):
    return JsonResponse({"error": message}, status=status)


def _traslado_to_json(traslado, incluir_detalles=False):
    data = {
        "id": traslado.id,
        "sucursal_origen": traslado.sucursal_origen_id,
        "sucursal_origen_nombre": str(traslado.sucursal_origen),
        "sucursal_destino": traslado.sucursal_destino_id,
        "sucursal_destino_nombre": str(traslado.sucursal_destino),
        "estado": traslado.estado,
        "observaciones": traslado.observaciones or "",
        "usuario_solicita": str(traslado.usuario_solicita),
        "usuario_envia": str(traslado.usuario_envia) if traslado.usuario_envia else None,
        "usuario_recibe": str(traslado.usuario_recibe) if traslado.usuario_recibe else None,
        "fecha_creacion": traslado.fecha_creacion.isoformat(),
        "fecha_envio": traslado.fecha_envio.isoformat() if traslado.fecha_envio else None,
        "fecha_recepcion": traslado.fecha_recepcion.isoformat() if traslado.fecha_recepcion else None,
    }

    if incluir_detalles:
        data["detalles"] = [
            {
                "id": detalle.id,
                "producto": detalle.producto_id,
                "producto_nombre": detalle.producto.nombre,
                "stock_origen": detalle.stock_origen_id,
                "lote": detalle.lote,
                "fecha_vencimiento": detalle.fecha_vencimiento.isoformat(),
                "cantidad": detalle.cantidad,
                "cantidad_recibida": detalle.cantidad_recibida,
                "stock_disponible": detalle.stock_origen.cantidad_disponible,
            }
            for detalle in traslado.detalles.select_related(
                "producto",
                "stock_origen",
            ).all()
        ]

    return data


@login_required
def traslados_home_view(request):
    traslados = TrasladoStock.objects.select_related(
        "sucursal_origen",
        "sucursal_destino",
        "usuario_solicita",
        "usuario_envia",
        "usuario_recibe",
    ).order_by("-fecha_creacion")

    return render(request, "traslados_templates/traslados_home.html", {
        "transferencias": traslados,
        "traslados": traslados,
    })


@login_required
def traslado_create_view(request):
    sucursales = Sucursal.objects.all().order_by("nombre")
    productos = Producto.objects.filter(activo=True).order_by("nombre")

    return render(request, "traslados_templates/traslado_form.html", {
        "sucursales": sucursales,
        "productos": productos,
        "modo": "crear",
    })


@login_required
def traslado_edit_view(request, transferencia_id):
    traslado = get_object_or_404(
        TrasladoStock.objects.select_related(
            "sucursal_origen",
            "sucursal_destino",
            "usuario_solicita",
        ),
        id=transferencia_id
    )

    if traslado.estado != "PENDIENTE":
        return render(request, "traslados_templates/traslado_form.html", {
            "error": "Solo puedes editar traslados en estado PENDIENTE.",
            "transferencia": traslado,
            "traslado": traslado,
            "modo": "editar",
        })

    sucursales = Sucursal.objects.all().order_by("nombre")
    productos = Producto.objects.filter(activo=True).order_by("nombre")

    return render(request, "traslados_templates/traslado_form.html", {
        "sucursales": sucursales,
        "productos": productos,
        "transferencia": traslado,
        "traslado": traslado,
        "modo": "editar",
    })


@login_required
@require_GET
def transferencias_list_api(request):
    traslados = TrasladoStock.objects.select_related(
        "sucursal_origen",
        "sucursal_destino",
        "usuario_solicita",
        "usuario_envia",
        "usuario_recibe",
    ).order_by("-fecha_creacion")

    data = [_traslado_to_json(t) for t in traslados]

    return JsonResponse({
        "count": len(data),
        "results": data,
    })


@login_required
@require_GET
def transferencia_detail_api(request, transferencia_id):
    traslado = get_object_or_404(
        TrasladoStock.objects.select_related(
            "sucursal_origen",
            "sucursal_destino",
            "usuario_solicita",
            "usuario_envia",
            "usuario_recibe",
        ).prefetch_related("detalles__producto", "detalles__stock_origen"),
        id=transferencia_id
    )

    return JsonResponse(_traslado_to_json(traslado, incluir_detalles=True))


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

    traslado = TrasladoStock.objects.create(
        sucursal_origen_id=sucursal_origen_id,
        sucursal_destino_id=sucursal_destino_id,
        usuario_solicita=request.user,
        observaciones=observaciones,
        estado="PENDIENTE",
    )

    for item in detalles:
        producto_id = item.get("producto")
        stock_origen_id = item.get("stock_origen")

        try:
            cantidad = int(item.get("cantidad") or 0)
        except ValueError:
            return _json_error("La cantidad enviada no es válida.", 400)

        if cantidad <= 0:
            return _json_error("La cantidad debe ser mayor a cero.", 400)

        stock = StockProducto.objects.select_for_update().select_related(
            "producto",
            "sucursal",
        ).filter(
            id=stock_origen_id,
            producto_id=producto_id,
            sucursal_id=sucursal_origen_id,
            activo=True,
        ).first()

        if not stock:
            return _json_error("El lote seleccionado no pertenece al producto o sucursal de origen.", 400)

        if stock.cantidad_disponible < cantidad:
            return _json_error(f"Stock insuficiente para {stock.producto.nombre}.", 400)

        DetalleTrasladoStock.objects.create(
            traslado=traslado,
            producto_id=producto_id,
            stock_origen=stock,
            lote=stock.lote,
            fecha_vencimiento=stock.fecha_vencimiento,
            cantidad=cantidad,
            cantidad_recibida=0,
        )

    return JsonResponse({
        "message": "Traslado creado correctamente.",
        "transferencia": _traslado_to_json(traslado, incluir_detalles=True),
        "traslado": _traslado_to_json(traslado, incluir_detalles=True),
    }, status=201)


@login_required
@require_http_methods(["PUT", "PATCH"])
@transaction.atomic
def transferencia_update_api(request, transferencia_id):
    traslado = get_object_or_404(TrasladoStock, id=transferencia_id)

    if traslado.estado != "PENDIENTE":
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

    traslado.sucursal_origen_id = sucursal_origen_id
    traslado.sucursal_destino_id = sucursal_destino_id
    traslado.observaciones = observaciones
    traslado.save()

    traslado.detalles.all().delete()

    for item in detalles:
        producto_id = item.get("producto")
        stock_origen_id = item.get("stock_origen")

        try:
            cantidad = int(item.get("cantidad") or 0)
        except ValueError:
            return _json_error("La cantidad enviada no es válida.", 400)

        if cantidad <= 0:
            return _json_error("La cantidad debe ser mayor a cero.", 400)

        stock = StockProducto.objects.select_for_update().select_related(
            "producto",
            "sucursal",
        ).filter(
            id=stock_origen_id,
            producto_id=producto_id,
            sucursal_id=sucursal_origen_id,
            activo=True,
        ).first()

        if not stock:
            return _json_error("El lote seleccionado no pertenece al producto o sucursal de origen.", 400)

        if stock.cantidad_disponible < cantidad:
            return _json_error(f"Stock insuficiente para {stock.producto.nombre}.", 400)

        DetalleTrasladoStock.objects.create(
            traslado=traslado,
            producto_id=producto_id,
            stock_origen=stock,
            lote=stock.lote,
            fecha_vencimiento=stock.fecha_vencimiento,
            cantidad=cantidad,
            cantidad_recibida=0,
        )

    return JsonResponse({
        "message": "Traslado actualizado correctamente.",
        "transferencia": _traslado_to_json(traslado, incluir_detalles=True),
        "traslado": _traslado_to_json(traslado, incluir_detalles=True),
    })


@login_required
@require_POST
@transaction.atomic
def transferencia_delete_api(request, transferencia_id):
    traslado = get_object_or_404(TrasladoStock, id=transferencia_id)

    if traslado.estado != "PENDIENTE":
        return _json_error("Solo puedes eliminar traslados en estado PENDIENTE.", 400)

    traslado.delete()

    return JsonResponse({
        "message": "Traslado eliminado correctamente."
    })


@login_required
@require_POST
@transaction.atomic
def transferencia_enviar_api(request, transferencia_id):
    traslado = get_object_or_404(
        TrasladoStock.objects.select_for_update().prefetch_related("detalles__stock_origen", "detalles__producto"),
        id=transferencia_id
    )

    if traslado.estado != "PENDIENTE":
        return _json_error("Solo puedes enviar traslados en estado PENDIENTE.", 400)

    detalles = traslado.detalles.select_related("producto", "stock_origen").all()

    if not detalles.exists():
        return _json_error("El traslado no tiene productos.", 400)

    for detalle in detalles:
        stock = StockProducto.objects.select_for_update().get(id=detalle.stock_origen_id)

        if stock.cantidad_disponible < detalle.cantidad:
            return _json_error(f"Stock insuficiente para {stock.producto.nombre}.", 400)

    for detalle in detalles:
        stock = StockProducto.objects.select_for_update().get(id=detalle.stock_origen_id)

        cantidad_anterior = stock.cantidad_disponible
        stock.cantidad_disponible -= detalle.cantidad
        stock.save(update_fields=["cantidad_disponible", "ultima_actualizacion"])

        MovimientoInventario.objects.create(
            producto=detalle.producto,
            sucursal=traslado.sucursal_origen,
            stock_afectado=stock,
            tipo_movimiento="TRASLADO_SALIDA",
            cantidad=detalle.cantidad,
            cantidad_anterior=cantidad_anterior,
            cantidad_nueva=stock.cantidad_disponible,
            sucursal_origen=traslado.sucursal_origen,
            sucursal_destino=traslado.sucursal_destino,
            usuario=request.user,
            referencia_doc=f"TRASLADO-{traslado.id}",
            observaciones=f"Salida por traslado #{traslado.id}",
        )

    traslado.estado = "ENVIADO"
    traslado.usuario_envia = request.user
    traslado.fecha_envio = timezone.now()
    traslado.save(update_fields=["estado", "usuario_envia", "fecha_envio"])

    return JsonResponse({
        "status": "Traslado enviado correctamente.",
        "traslado": _traslado_to_json(traslado, incluir_detalles=True),
    })


@login_required
@require_POST
@transaction.atomic
def transferencia_recibir_api(request, transferencia_id):
    traslado = get_object_or_404(
        TrasladoStock.objects.select_for_update().prefetch_related("detalles__stock_origen", "detalles__producto"),
        id=transferencia_id
    )

    if traslado.estado != "ENVIADO":
        return _json_error("Solo puedes recibir traslados en estado ENVIADO.", 400)

    detalles = traslado.detalles.select_related("producto", "stock_origen").all()

    if not detalles.exists():
        return _json_error("El traslado no tiene productos.", 400)

    for detalle in detalles:
        stock_destino, _ = StockProducto.objects.select_for_update().get_or_create(
            producto=detalle.producto,
            sucursal=traslado.sucursal_destino,
            lote=detalle.lote,
            defaults={
                "fecha_vencimiento": detalle.fecha_vencimiento,
                "cantidad_disponible": 0,
                "cantidad_reservada": 0,
                "precio_compra": detalle.stock_origen.precio_compra,
                "ubicacion_almacen": "",
                "activo": True,
            }
        )

        cantidad_anterior = stock_destino.cantidad_disponible
        stock_destino.cantidad_disponible += detalle.cantidad
        stock_destino.fecha_vencimiento = detalle.fecha_vencimiento
        stock_destino.activo = True
        stock_destino.save(update_fields=[
            "cantidad_disponible",
            "fecha_vencimiento",
            "activo",
            "ultima_actualizacion",
        ])

        detalle.cantidad_recibida = detalle.cantidad
        detalle.save(update_fields=["cantidad_recibida"])

        MovimientoInventario.objects.create(
            producto=detalle.producto,
            sucursal=traslado.sucursal_destino,
            stock_afectado=stock_destino,
            tipo_movimiento="TRASLADO_ENTRADA",
            cantidad=detalle.cantidad,
            cantidad_anterior=cantidad_anterior,
            cantidad_nueva=stock_destino.cantidad_disponible,
            sucursal_origen=traslado.sucursal_origen,
            sucursal_destino=traslado.sucursal_destino,
            usuario=request.user,
            referencia_doc=f"TRASLADO-{traslado.id}",
            observaciones=f"Entrada por traslado #{traslado.id}",
        )

    traslado.estado = "RECIBIDO"
    traslado.usuario_recibe = request.user
    traslado.fecha_recepcion = timezone.now()
    traslado.save(update_fields=["estado", "usuario_recibe", "fecha_recepcion"])

    return JsonResponse({
        "status": "Traslado recibido correctamente.",
        "traslado": _traslado_to_json(traslado, incluir_detalles=True),
    })