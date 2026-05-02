# ventas/views.py

import json
import inspect
from decimal import Decimal, InvalidOperation
from django.shortcuts import render
from django.http import HttpResponse, Http404, JsonResponse
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.views.decorators.http import require_GET, require_POST
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db.models import Q
from weasyprint import HTML
from .models import Venta, DetalleVenta, SesionCaja
from clientes.models import Cliente
from inventario.models import Producto




from clientes.models import Cliente

@login_required
def pos_view(request):
    tipos_documento = Cliente._meta.get_field('tipo_documento').choices

    return render(request, 'ventas_templates/pos.html', {
        'tipos_documento': tipos_documento,
    })

@login_required
def venta_list_view(request):
    return render(request, 'ventas_templates/venta_list.html')

@login_required
def generar_comprobante_pdf(request, venta_id):
    try:
        venta = Venta.objects.select_related(
            'cliente',
            'vendedor',
            'sucursal__farmacia'
        ).prefetch_related('detalles__producto').get(pk=venta_id)

        sucursal = venta.sucursal
        empresa = venta.sucursal.farmacia

        context = {
            'venta': venta,
            'detalles': venta.detalles.all(),
            'empresa': empresa,
            'sucursal': sucursal,
        }

        html_string = render_to_string(
            'ventas_templates/comprobante_template.html',
            context
        )

        print("DEBUG: Usando la clase HTML:", HTML)
        print("DEBUG: Ubicación del archivo:", inspect.getfile(HTML))

        pdf_file = HTML(
            string=html_string,
            base_url=request.build_absolute_uri()
        ).write_pdf()

        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="comprobante_venta_{venta.id}.pdf"'
        return response

    except Venta.DoesNotExist:
        raise Http404("La venta especificada no existe.")
    except Exception as e:
        return HttpResponse(
            f"Ocurrió un error al generar el PDF: {e}",
            status=500
        )

def _json_body(request):
    try:
        return json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return None

def _decimal(value, default="0.00"):
    try:
        if value in [None, ""]:
            return Decimal(default)
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return Decimal(default)

def _obtener_sucursal_usuario(user):
    """
    Ajusta esta función según tu modelo Usuario.
    Primero intenta user.sucursal.
    Luego intenta user.perfil.sucursal.
    """
    sucursal = getattr(user, "sucursal", None)

    if sucursal:
        return sucursal

    perfil = getattr(user, "perfil", None)
    if perfil and getattr(perfil, "sucursal", None):
        return perfil.sucursal

    return None


def _json_error(message, status=400):
    return JsonResponse({"error": message}, status=status)

@login_required
@require_GET
def estado_caja_api(request):
    sucursal = _obtener_sucursal_usuario(request.user)

    if not sucursal:
        return _json_error("El usuario no tiene una sucursal asignada.", 400)

    sesion = SesionCaja.objects.filter(
        usuario=request.user,
        sucursal=sucursal,
        estado="ABIERTA"
    ).first()

    if not sesion:
        return _json_error("CAJA_CERRADA", 404)

    return JsonResponse({
        "id": sesion.id,
        "estado": sesion.estado,
        "monto_inicial": str(sesion.monto_inicial),
        "fecha_apertura": sesion.fecha_apertura.strftime("%Y-%m-%d %H:%M:%S"),
        "sucursal": str(sesion.sucursal),
    })

@login_required
@require_POST
@transaction.atomic
def abrir_caja_api(request):
    data = _json_body(request)

    if data is None:
        return _json_error("JSON inválido.", 400)

    sucursal = _obtener_sucursal_usuario(request.user)

    if not sucursal:
        return _json_error("El usuario no tiene una sucursal asignada.", 400)

    monto_inicial = _decimal(data.get("monto_inicial"))

    if monto_inicial < 0:
        return _json_error("El monto inicial no puede ser negativo.", 400)

    if SesionCaja.objects.filter(
        usuario=request.user,
        sucursal=sucursal,
        estado="ABIERTA"
    ).exists():
        return _json_error("Ya tienes una caja abierta en esta sucursal.", 400)

    sesion = SesionCaja.objects.create(
        usuario=request.user,
        sucursal=sucursal,
        monto_inicial=monto_inicial,
        estado="ABIERTA"
    )

    return JsonResponse({
        "id": sesion.id,
        "estado": sesion.estado,
        "monto_inicial": str(sesion.monto_inicial),
        "fecha_apertura": sesion.fecha_apertura.strftime("%Y-%m-%d %H:%M:%S"),
    }, status=201)


@login_required
@require_POST
@transaction.atomic
def cerrar_caja_api(request):
    data = _json_body(request)

    if data is None:
        return _json_error("JSON inválido.", 400)

    sucursal = _obtener_sucursal_usuario(request.user)

    if not sucursal:
        return _json_error("El usuario no tiene una sucursal asignada.", 400)

    sesion = SesionCaja.objects.filter(
        usuario=request.user,
        sucursal=sucursal,
        estado="ABIERTA"
    ).first()

    if not sesion:
        return _json_error("No tienes una caja abierta para cerrar.", 404)

    monto_final_real = _decimal(data.get("monto_final_real"))
    observaciones = data.get("observaciones", "")

    if monto_final_real < 0:
        return _json_error("El monto final real no puede ser negativo.", 400)

    total_efectivo = Venta.objects.filter(
        sesion_caja=sesion,
        estado="COMPLETADA",
        metodo_pago="EFECTIVO"
    ).aggregate(
        total=Sum("total_venta")
    )["total"] or Decimal("0.00")

    monto_final_sistema = sesion.monto_inicial + total_efectivo
    diferencia = monto_final_real - monto_final_sistema

    sesion.monto_final_sistema = monto_final_sistema
    sesion.monto_final_real = monto_final_real
    sesion.diferencia = diferencia
    sesion.fecha_cierre = timezone.now()
    sesion.estado = "CERRADA"
    sesion.observaciones = observaciones
    sesion.save()

    return JsonResponse({
        "id": sesion.id,
        "estado": sesion.estado,
        "monto_inicial": str(sesion.monto_inicial),
        "monto_final_sistema": str(sesion.monto_final_sistema),
        "monto_final_real": str(sesion.monto_final_real),
        "diferencia": str(sesion.diferencia),
        "fecha_cierre": sesion.fecha_cierre.strftime("%Y-%m-%d %H:%M:%S"),
    })


@login_required
@require_GET
def ventas_list_api(request):
    ventas = Venta.objects.select_related(
        'cliente',
        'vendedor',
        'sucursal'
    ).order_by('-fecha_venta')

    search = request.GET.get('search', '').strip()
    fecha_inicio = request.GET.get('fecha_venta__date__gte')
    fecha_fin = request.GET.get('fecha_venta__date__lte')

    if search:
        ventas = ventas.filter(
            Q(cliente__nombres__icontains=search) |
            Q(cliente__apellidos__icontains=search) |
            Q(vendedor__username__icontains=search) |
            Q(tipo_comprobante__icontains=search) |
            Q(numero_comprobante__icontains=search)
        )

    if fecha_inicio:
        ventas = ventas.filter(fecha_venta__date__gte=fecha_inicio)

    if fecha_fin:
        ventas = ventas.filter(fecha_venta__date__lte=fecha_fin)

    paginator = Paginator(ventas, 10)
    page_number = request.GET.get('page', 1)
    page = paginator.get_page(page_number)

    results = []

    for venta in page.object_list:
        cliente_nombre = 'Público General'
        if venta.cliente:
            cliente_nombre = str(venta.cliente)

        results.append({
            'id': venta.id,
            'fecha_venta': venta.fecha_venta.isoformat() if venta.fecha_venta else '',
            'cliente_nombre_completo': cliente_nombre,
            'vendedor_username': venta.vendedor.username if venta.vendedor else '',
            'tipo_comprobante': venta.tipo_comprobante,
            'serie_comprobante': getattr(venta, 'serie_comprobante', '') or '',
            'numero_comprobante': getattr(venta, 'numero_comprobante', '') or '',
            'total_venta': str(venta.total_venta),
            'estado': venta.estado,
            'metodo_pago': venta.metodo_pago,
        })

    base_url = request.build_absolute_uri(request.path)
    query_params = request.GET.copy()

    def build_page_url(page_num):
        query_params['page'] = page_num
        return f"{base_url}?{query_params.urlencode()}"

    return JsonResponse({
        'count': paginator.count,
        'results': results,
        'next': build_page_url(page.next_page_number()) if page.has_next() else None,
        'previous': build_page_url(page.previous_page_number()) if page.has_previous() else None,
    })


@login_required
@require_GET
def venta_detail_api(request, venta_id):
    try:
        venta = Venta.objects.select_related(
            'cliente',
            'vendedor',
            'sucursal'
        ).prefetch_related('detalles__producto').get(id=venta_id)
    except Venta.DoesNotExist:
        return _json_error('La venta no existe.', 404)

    cliente_nombre = 'Público General'
    if venta.cliente:
        cliente_nombre = str(venta.cliente)

    detalles = []

    for detalle in venta.detalles.all():
        detalles.append({
            'producto_nombre': detalle.producto.nombre if detalle.producto else '',
            'cantidad': str(detalle.cantidad),
            'precio_unitario': str(detalle.precio_unitario),
            'monto_descuento_linea': str(detalle.monto_descuento_linea),
            'subtotal': str(detalle.subtotal_linea),
        })

    return JsonResponse({
        'id': venta.id,
        'fecha_venta': venta.fecha_venta.isoformat() if venta.fecha_venta else '',
        'cliente_nombre_completo': cliente_nombre,
        'vendedor_username': venta.vendedor.username if venta.vendedor else '',
        'tipo_comprobante': venta.tipo_comprobante,
        'serie_comprobante': getattr(venta, 'serie_comprobante', '') or '',
        'numero_comprobante': getattr(venta, 'numero_comprobante', '') or '',
        'metodo_pago': venta.metodo_pago,
        'estado': venta.estado,
        'subtotal_venta': str(getattr(venta, 'subtotal', 0)),
        'monto_igv': str(getattr(venta, 'impuestos', 0)),
        'total_venta': str(venta.total_venta),
        'detalles': detalles,
    })

@login_required
@require_POST
def registrar_venta_api(request):
    data = _json_body(request)

    if data is None:
        return _json_error("JSON inválido.", 400)

    try:
        with transaction.atomic():
            sucursal = _obtener_sucursal_usuario(request.user)

            if not sucursal:
                return _json_error("El usuario no tiene una sucursal asignada.", 400)

            sesion = SesionCaja.objects.filter(
                usuario=request.user,
                sucursal=sucursal,
                estado="ABIERTA"
            ).first()

            if not sesion:
                return _json_error("Debes abrir caja antes de registrar una venta.", 400)

            detalles = data.get("detalles", [])

            if not detalles:
                return _json_error("La venta no tiene productos.", 400)

            cliente = None
            cliente_id = data.get("cliente")

            if cliente_id:
                cliente = Cliente.objects.filter(id=cliente_id).first()
                if not cliente:
                    return _json_error("El cliente seleccionado no existe.", 400)

            tipo_comprobante = data.get("tipo_comprobante", "TICKET")
            metodo_pago = data.get("metodo_pago", "EFECTIVO")
            monto_recibido = _decimal(data.get("monto_recibido"))
            vuelto = _decimal(data.get("vuelto"))

            venta = Venta.objects.create(
                sucursal=sucursal,
                cliente=cliente,
                vendedor=request.user,
                sesion_caja=sesion,
                tipo_comprobante=tipo_comprobante,
                metodo_pago=metodo_pago,
                monto_recibido=monto_recibido,
                vuelto=vuelto,
                estado="COMPLETADA",
            )

            for item in detalles:
                producto_id = item.get("producto")

                producto = Producto.objects.filter(id=producto_id).first()
                if not producto:
                    raise ValueError(f"Producto inválido: {producto_id}")

                cantidad = _decimal(item.get("cantidad"), "1.00")
                precio_unitario = _decimal(item.get("precio_unitario"))
                descuento = _decimal(item.get("monto_descuento_linea"))
                unidad_venta = item.get("unidad_venta", "UNIDAD")

                if cantidad <= 0:
                    raise ValueError(
                        f"La cantidad del producto {producto.nombre} debe ser mayor a cero."
                    )

                if precio_unitario <= 0:
                    raise ValueError(
                        f"El producto {producto.nombre} no tiene precio válido."
                    )

                if descuento < 0:
                    raise ValueError(
                        f"El descuento del producto {producto.nombre} no puede ser negativo."
                    )

                subtotal_linea = (cantidad * precio_unitario) - descuento

                if subtotal_linea < 0:
                    raise ValueError(
                        f"El descuento del producto {producto.nombre} no puede superar el subtotal."
                    )

                detalle = DetalleVenta.objects.create(
                    venta=venta,
                    producto=producto,
                    cantidad=cantidad,
                    unidad_venta=unidad_venta,
                    precio_unitario=precio_unitario,
                    monto_descuento_linea=descuento,
                    subtotal_linea=subtotal_linea,
                )

                detalle.actualizar_stock_por_venta()

            venta.actualizar_totales()

            return JsonResponse({
                "id": venta.id,
                "tipo_comprobante": venta.tipo_comprobante,
                "total_venta": str(venta.total_venta),
                "subtotal": str(venta.subtotal),
                "impuestos": str(venta.impuestos),
                "metodo_pago": venta.metodo_pago,
                "cliente_telefono": venta.cliente.telefono if venta.cliente else "",
                "mensaje": "Venta registrada correctamente.",
            }, status=201)

    except ValidationError as e:
        return _json_error(str(e), 400)

    except ValueError as e:
        return _json_error(str(e), 400)

    except Exception as e:
        return _json_error(f"Error interno al registrar la venta: {e}", 500)
    
    
