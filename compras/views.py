from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404

from proveedores.models import Proveedor
from core.models import Sucursal
from inventario.models import Producto, UnidadPresentacion
from .models import Compra, DetalleCompra


def compras_home_view(request):
    query = request.GET.get('q', '').strip()

    compras = Compra.objects.select_related(
        'proveedor',
        'sucursal_destino',
        'registrado_por'
    ).order_by('-fecha_recepcion', '-id')

    if query:
        compras = compras.filter(
            Q(numero_factura_proveedor__icontains=query) |
            Q(proveedor__nombre_comercial__icontains=query) |
            Q(sucursal_destino__nombre__icontains=query) |
            Q(estado__icontains=query)
        )

    paginator = Paginator(compras, 7)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'compras_templates/compras_home.html', {
        'compras': page_obj,
        'query': query,
        'total_compras': compras.count(),
    })


def _to_decimal(value, default='0'):
    try:
        return Decimal(str(value or default))
    except (InvalidOperation, TypeError):
        return Decimal(default)


def compra_create_view(request):
    return compra_form_view(request)


def compra_edit_view(request, pk):
    compra = get_object_or_404(
        Compra.objects.prefetch_related(
            'detalles__producto',
            'detalles__presentacion'
        ),
        pk=pk
    )
    return compra_form_view(request, compra)


def compra_form_view(request, compra=None):
    proveedores = Proveedor.objects.filter(activo=True).order_by('nombre_comercial')
    sucursales = Sucursal.objects.all().order_by('nombre')
    productos = Producto.objects.select_related('laboratorio').order_by('nombre')
    presentaciones = UnidadPresentacion.objects.all().order_by('nombre')

    productos_data = []
    unidad_default = presentaciones.filter(nombre__iexact='unidad').first()

    for p in productos:
        productos_data.append({
            'id': p.id,
            'nombre': p.nombre,
            'concentracion': getattr(p, 'concentracion', '') or '',
            'laboratorio': p.laboratorio.nombre if getattr(p, 'laboratorio', None) else '',
            'lote': getattr(p, 'lote', '') or '',
            'fecha_vencimiento': str(getattr(p, 'fecha_vencimiento', '') or ''),
            'precio': str(
                getattr(p, 'precio_venta_sugerido', None)
                or getattr(p, 'precio_venta', None)
                or getattr(p, 'precio_compra', None)
                or '0.00'
            ),
            'presentacion_id': (
                getattr(p, 'presentacion_id', None)
                or getattr(p, 'unidad_presentacion_id', None)
                or getattr(p, 'unidad_id', None)
                or (unidad_default.id if unidad_default else None)
            ),
        })

    if compra and compra.estado != 'PENDIENTE':
        messages.warning(request, 'Esta compra ya fue procesada o anulada. No puede modificarse.')
        return redirect('compras:home')

    if request.method == 'POST':
        proveedor_id = request.POST.get('proveedor')
        sucursal_id = request.POST.get('sucursal_destino')
        numero_factura = request.POST.get('numero_factura_proveedor', '').strip()
        accion = request.POST.get('accion', 'guardar')

        productos_ids = request.POST.getlist('producto')
        presentaciones_ids = request.POST.getlist('presentacion')
        lotes = request.POST.getlist('lote')
        fechas = request.POST.getlist('fecha_vencimiento')
        cantidades = request.POST.getlist('cantidad_recibida')
        precios = request.POST.getlist('precio_unitario_compra')

        errores = []
        detalles_limpios = []

        if not proveedor_id:
            errores.append('Selecciona un proveedor.')
        if not sucursal_id:
            errores.append('Selecciona una sucursal destino.')
        if not numero_factura:
            errores.append('Ingresa el número de factura.')

        for i, producto_id in enumerate(productos_ids):
            if not producto_id:
                continue

            cantidad = _to_decimal(cantidades[i] if i < len(cantidades) else 0)
            precio = _to_decimal(precios[i] if i < len(precios) else 0)
            lote = lotes[i].strip() if i < len(lotes) else ''
            fecha = fechas[i] if i < len(fechas) else ''
            presentacion_id = presentaciones_ids[i] if i < len(presentaciones_ids) else None

            if cantidad <= 0:
                errores.append('La cantidad debe ser mayor a 0.')
            if precio < 0:
                errores.append('El precio unitario no puede ser negativo.')
            if not lote:
                errores.append('Todos los productos deben tener lote.')
            if not fecha:
                errores.append('Todos los productos deben tener fecha de vencimiento.')

            detalles_limpios.append({
                'producto_id': producto_id,
                'presentacion_id': presentacion_id or None,
                'lote': lote,
                'fecha_vencimiento': fecha,
                'cantidad_recibida': cantidad,
                'precio_unitario_compra': precio,
            })

        if not detalles_limpios:
            errores.append('Agrega al menos un producto válido.')

        if errores:
            for error in errores:
                messages.error(request, error)
        else:
            with transaction.atomic():
                if compra is None:
                    compra = Compra(registrado_por=request.user)

                compra.proveedor_id = proveedor_id
                compra.sucursal_destino_id = sucursal_id
                compra.numero_factura_proveedor = numero_factura
                compra.save()

                compra.detalles.all().delete()

                for item in detalles_limpios:
                    DetalleCompra.objects.create(
                        compra=compra,
                        producto_id=item['producto_id'],
                        presentacion_id=item['presentacion_id'],
                        lote=item['lote'],
                        fecha_vencimiento=item['fecha_vencimiento'],
                        cantidad_recibida=item['cantidad_recibida'],
                        precio_unitario_compra=item['precio_unitario_compra'],
                    )

                compra.calcular_totales()

                if accion == 'procesar':
                    for detalle in compra.detalles.all():
                        detalle.actualizar_stock_por_compra(request.user)

                    compra.estado = 'PROCESADA'
                    compra.save()
                    messages.success(request, f'La compra #{compra.id} fue registrada y procesada correctamente.')
                else:
                    messages.success(request, f'La compra #{compra.id} fue guardada correctamente.')

                return redirect('compras:home')

    return render(request, 'compras_templates/compra_form.html', {
        'compra': compra,
        'proveedores': proveedores,
        'sucursales': sucursales,
        'productos': productos,
        'productos_data': productos_data,
        'presentaciones': presentaciones,
    })


def compra_delete_view(request, pk):
    compra = get_object_or_404(Compra, pk=pk)

    if request.method == 'POST':
        compra_id = compra.id
        compra.delete()
        messages.success(request, f'La compra #{compra_id} fue eliminada correctamente.')
        return redirect('compras:home')

    return render(request, 'compras_templates/compra_eliminar.html', {
        'compra': compra
    })