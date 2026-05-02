from decimal import Decimal, InvalidOperation
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Subquery, OuterRef, IntegerField, ProtectedError, Q
from django.db.models.functions import Coalesce
from django.db import IntegrityError
from django.core.paginator import Paginator

from .models import (
    CategoriaProducto, Laboratorio, FormaFarmaceutica,
    PrincipioActivo, Producto, StockProducto,
    Sucursal, MovimientoInventario, UnidadPresentacion
)


def inventario_home_view(request):
    return HttpResponse("<h1>Gestión de Inventario</h1><p>Esta es la página de inicio de la aplicación de inventario. Aquí podrás ver y gestionar productos y stock.</p>")


def categoria_list_view(request):
    lista_de_categorias = CategoriaProducto.objects.all().order_by('nombre')
    return render(request, 'inventario_templates/categoria_list.html', {'categorias': lista_de_categorias})


def categoria_create_view(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion', '')
        if nombre:
            CategoriaProducto.objects.create(nombre=nombre, descripcion=descripcion)
            messages.success(request, 'La categoría ha sido creada con éxito.')
            return redirect('inventario:categoria_list')
    return render(request, 'inventario_templates/categoria_form.html')


def categoria_update_view(request, pk):
    categoria = get_object_or_404(CategoriaProducto, pk=pk)
    if request.method == 'POST':
        categoria.nombre = request.POST.get('nombre')
        categoria.descripcion = request.POST.get('descripcion', '')
        categoria.save()
        messages.success(request, f"La categoría '{categoria.nombre}' ha sido actualizada con éxito.")
        return redirect('inventario:categoria_list')
    return render(request, 'inventario_templates/categoria_form.html', {'categoria': categoria})


@require_POST
def categoria_delete_view(request, pk):
    categoria = get_object_or_404(CategoriaProducto, pk=pk)
    try:
        categoria.delete()
        messages.success(request, f"La categoría '{categoria.nombre}' ha sido eliminada con éxito.")
    except ProtectedError:
        messages.error(request, f"La categoría '{categoria.nombre}' no se puede eliminar porque tiene productos asociados.")
    return redirect('inventario:categoria_list')


def laboratorio_list_view(request):
    lista_de_laboratorios = Laboratorio.objects.all().order_by('nombre')
    return render(request, 'inventario_templates/laboratorio_list.html', {'laboratorios': lista_de_laboratorios})


def laboratorio_create_view(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        if nombre:
            Laboratorio.objects.create(nombre=nombre)
            messages.success(request, 'El laboratorio ha sido creado con éxito.')
            return redirect('inventario:laboratorio_list')
    return render(request, 'inventario_templates/laboratorio_form.html')


def laboratorio_update_view(request, pk):
    laboratorio = get_object_or_404(Laboratorio, pk=pk)
    if request.method == 'POST':
        laboratorio.nombre = request.POST.get('nombre')
        laboratorio.save()
        messages.success(request, f"El laboratorio '{laboratorio.nombre}' ha sido actualizado con éxito.")
        return redirect('inventario:laboratorio_list')
    return render(request, 'inventario_templates/laboratorio_form.html', {'laboratorio': laboratorio})


@require_POST
def laboratorio_delete_view(request, pk):
    laboratorio = get_object_or_404(Laboratorio, pk=pk)
    try:
        laboratorio.delete()
        messages.success(request, f"El laboratorio '{laboratorio.nombre}' ha sido eliminado con éxito.")
    except ProtectedError:
        messages.error(request, f"El laboratorio '{laboratorio.nombre}' no se puede eliminar porque tiene productos asociados.")
    return redirect('inventario:laboratorio_list')


def forma_farmaceutica_list_view(request):
    lista = FormaFarmaceutica.objects.all().order_by('nombre')
    return render(request, 'inventario_templates/forma_farmaceutica_list.html', {'formas_farmaceuticas': lista})


def forma_farmaceutica_create_view(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        if nombre:
            FormaFarmaceutica.objects.create(nombre=nombre)
            messages.success(request, 'La forma farmacéutica ha sido creada con éxito.')
            return redirect('inventario:forma_farmaceutica_list')
    return render(request, 'inventario_templates/forma_farmaceutica_form.html')


def forma_farmaceutica_update_view(request, pk):
    item = get_object_or_404(FormaFarmaceutica, pk=pk)
    if request.method == 'POST':
        item.nombre = request.POST.get('nombre')
        item.save()
        messages.success(request, f"La forma farmacéutica '{item.nombre}' ha sido actualizada con éxito.")
        return redirect('inventario:forma_farmaceutica_list')
    return render(request, 'inventario_templates/forma_farmaceutica_form.html', {'forma_farmaceutica': item})


@require_POST
def forma_farmaceutica_delete_view(request, pk):
    item = get_object_or_404(FormaFarmaceutica, pk=pk)
    try:
        item.delete()
        messages.success(request, f"La forma farmacéutica '{item.nombre}' ha sido eliminada con éxito.")
    except ProtectedError:
        messages.error(request, f"La forma farmacéutica '{item.nombre}' no se puede eliminar porque tiene productos asociados.")
    return redirect('inventario:forma_farmaceutica_list')


def principio_activo_list_view(request):
    lista = PrincipioActivo.objects.all().order_by('nombre')
    return render(request, 'inventario_templates/principio_activo_list.html', {'principios_activos': lista})


def principio_activo_create_view(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        if nombre:
            PrincipioActivo.objects.create(nombre=nombre)
            messages.success(request, 'El principio activo ha sido creado con éxito.')
            return redirect('inventario:principio_activo_list')
    return render(request, 'inventario_templates/principio_activo_form.html')


def principio_activo_update_view(request, pk):
    item = get_object_or_404(PrincipioActivo, pk=pk)
    if request.method == 'POST':
        item.nombre = request.POST.get('nombre')
        item.save()
        messages.success(request, f"El principio activo '{item.nombre}' ha sido actualizado con éxito.")
        return redirect('inventario:principio_activo_list')
    return render(request, 'inventario_templates/principio_activo_form.html', {'principio_activo': item})


@require_POST
def principio_activo_delete_view(request, pk):
    item = get_object_or_404(PrincipioActivo, pk=pk)
    try:
        item.delete()
        messages.success(request, f"El principio activo '{item.nombre}' ha sido eliminado con éxito.")
    except ProtectedError:
        messages.error(request, f"El principio activo '{item.nombre}' no se puede eliminar porque tiene productos asociados.")
    return redirect('inventario:principio_activo_list')


def producto_list_view(request):
    stock_subquery = StockProducto.objects.filter(producto=OuterRef('pk'))
    user = request.user

    if hasattr(user, 'rol') and user.rol and user.rol.nombre == 'Gerente de Sucursal' and hasattr(user, 'sucursal') and user.sucursal:
        stock_subquery = stock_subquery.filter(sucursal=user.sucursal)

    stock_total_subquery = stock_subquery.values('producto').annotate(
        total_stock=Sum('cantidad')
    ).values('total_stock')

    lista_productos = Producto.objects.select_related('categoria', 'laboratorio').annotate(
        stock_sucursal=Coalesce(Subquery(stock_total_subquery, output_field=IntegerField()), 0)
    ).order_by('nombre')

    return render(request, 'inventario_templates/producto_list.html', {'productos': lista_productos})


def producto_form_view(request, pk=None):
    producto = get_object_or_404(Producto, pk=pk) if pk else None

    categorias = CategoriaProducto.objects.all().order_by('nombre')
    laboratorios = Laboratorio.objects.all().order_by('nombre')
    principios = PrincipioActivo.objects.all().order_by('nombre')
    formas = FormaFarmaceutica.objects.all().order_by('nombre')
    unidades = UnidadPresentacion.objects.all().order_by('nombre')

    if request.method == 'POST':
        nombre = (request.POST.get('nombre') or '').strip()
        descripcion = (request.POST.get('descripcion') or '').strip()
        codigo_barras = (request.POST.get('codigo_barras') or '').strip() or None
        concentracion = (request.POST.get('concentracion') or '').strip()

        categoria_id = request.POST.get('categoria') or None
        laboratorio_id = request.POST.get('laboratorio') or None
        principio_activo_id = request.POST.get('principio_activo') or None
        forma_farmaceutica_id = request.POST.get('forma_farmaceutica') or None
        unidad_compra_id = request.POST.get('unidad_compra') or None
        unidad_venta_id = request.POST.get('unidad_venta') or None

        precio_venta_sugerido = request.POST.get('precio_venta_sugerido') or '0'
        margen_ganancia_sugerido = request.POST.get('margen_ganancia_sugerido') or '0.20'
        unidades_por_caja = request.POST.get('unidades_por_caja') or '1'
        unidades_por_blister = request.POST.get('unidades_por_blister') or '1'

        aplica_receta = request.POST.get('aplica_receta') == 'on'
        es_controlado = request.POST.get('es_controlado') == 'on'

        errores = []

        if not nombre:
            errores.append('El nombre del producto es obligatorio.')
        if not categoria_id:
            errores.append('La categoría es obligatoria.')
        if not laboratorio_id:
            errores.append('El laboratorio es obligatorio.')
        if not forma_farmaceutica_id:
            errores.append('La forma farmacéutica es obligatoria.')

        try:
            precio_venta_sugerido = Decimal(str(precio_venta_sugerido))
        except (InvalidOperation, TypeError):
            errores.append('El precio de venta sugerido no es válido.')

        try:
            margen_ganancia_sugerido = Decimal(str(margen_ganancia_sugerido))
        except (InvalidOperation, TypeError):
            errores.append('El margen de ganancia sugerido no es válido.')

        try:
            unidades_por_caja = int(unidades_por_caja)
            if unidades_por_caja < 1:
                errores.append('Las unidades por caja deben ser mayores o iguales a 1.')
        except (ValueError, TypeError):
            errores.append('Las unidades por caja no son válidas.')

        try:
            unidades_por_blister = int(unidades_por_blister)
            if unidades_por_blister < 1:
                errores.append('Las unidades por blíster deben ser mayores o iguales a 1.')
        except (ValueError, TypeError):
            errores.append('Las unidades por blíster no son válidas.')

        if errores:
            for error in errores:
                messages.error(request, error)
        else:
            try:
                if producto is None:
                    producto = Producto()

                producto.nombre = nombre
                producto.descripcion = descripcion
                producto.codigo_barras = codigo_barras
                producto.concentracion = concentracion
                producto.categoria_id = categoria_id
                producto.laboratorio_id = laboratorio_id
                producto.principio_activo_id = principio_activo_id
                producto.forma_farmaceutica_id = forma_farmaceutica_id
                producto.unidad_compra_id = unidad_compra_id
                producto.unidad_venta_id = unidad_venta_id
                producto.precio_venta_sugerido = precio_venta_sugerido
                producto.margen_ganancia_sugerido = margen_ganancia_sugerido
                producto.unidades_por_caja = unidades_por_caja
                producto.unidades_por_blister = unidades_por_blister
                producto.aplica_receta = aplica_receta
                producto.es_controlado = es_controlado

                if request.FILES.get('imagen_producto'):
                    producto.imagen_producto = request.FILES.get('imagen_producto')

                producto.save()

                if pk:
                    messages.success(request, f"El producto '{producto.nombre}' ha sido actualizado con éxito.")
                else:
                    messages.success(request, f"El producto '{producto.nombre}' ha sido creado con éxito.")

                return redirect('inventario:producto_list')

            except IntegrityError:
                messages.error(request, 'Ya existe un producto con ese código de barras.')

    context = {
        'producto': producto,
        'categorias': categorias,
        'laboratorios': laboratorios,
        'principios': principios,
        'formas': formas,
        'unidades': unidades,
    }
    return render(request, 'inventario_templates/producto_form.html', context)


def producto_detail_view(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        sucursal_id = request.POST.get('sucursal')
        lote = request.POST.get('lote')
        cantidad = int(request.POST.get('cantidad', 0))

        stock, created = StockProducto.objects.get_or_create(
            producto=producto,
            sucursal_id=sucursal_id,
            lote=lote,
            defaults={
                'fecha_vencimiento': request.POST.get('fecha_vencimiento'),
                'precio_compra': request.POST.get('precio_compra') or 0,
                'precio_venta': request.POST.get('precio_venta') or 0,
                'ubicacion_almacen': request.POST.get('ubicacion_almacen', '')
            }
        )

        if not created:
            stock.cantidad += cantidad
            stock.save()
        else:
            stock.cantidad = cantidad
            stock.save()

        MovimientoInventario.objects.create(
            producto=producto,
            sucursal_id=sucursal_id,
            stock_afectado=stock,
            tipo_movimiento='ENTRADA',
            cantidad=cantidad,
            usuario=request.user,
            referencia_doc=f"Compra Lote {lote}"
        )
        messages.success(request, f"Se ha añadido stock para '{producto.nombre}' con éxito.")
        return redirect('inventario:producto_detail', pk=pk)

    stock_items = StockProducto.objects.filter(
        producto=producto
    ).select_related('sucursal').order_by('fecha_vencimiento')

    paginator = Paginator(stock_items, 6)
    page_number = request.GET.get('page')
    stock_page = paginator.get_page(page_number)

    return render(request, 'inventario_templates/producto_detail.html', {
        'producto': producto,
        'stock_items': stock_page,
        'stock_total': stock_items.count(),
        'sucursales': Sucursal.objects.all()
    })


def unidad_presentacion_list_view(request):
    lista = UnidadPresentacion.objects.select_related('padre').all().order_by('nombre')
    return render(request, 'inventario_templates/unidad_presentacion_list.html', {'unidades': lista})


def unidad_presentacion_create_view(request):
    if request.method == 'POST':
        UnidadPresentacion.objects.create(
            nombre=request.POST.get('nombre'),
            padre_id=request.POST.get('padre') or None
        )
        messages.success(request, 'La unidad de presentación ha sido creada.')
        return redirect('inventario:unidad_presentacion_list')
    return render(request, 'inventario_templates/unidad_presentacion_form.html', {
        'unidades_padre': UnidadPresentacion.objects.all()
    })


def unidad_presentacion_update_view(request, pk):
    item = get_object_or_404(UnidadPresentacion, pk=pk)
    if request.method == 'POST':
        item.nombre = request.POST.get('nombre')
        item.padre_id = request.POST.get('padre') or None
        item.save()
        messages.success(request, f"La unidad '{item.nombre}' ha sido actualizada.")
        return redirect('inventario:unidad_presentacion_list')
    return render(request, 'inventario_templates/unidad_presentacion_form.html', {
        'unidad': item,
        'unidades_padre': UnidadPresentacion.objects.exclude(pk=pk)
    })


@require_POST
def unidad_presentacion_delete_view(request, pk):
    item = get_object_or_404(UnidadPresentacion, pk=pk)
    try:
        item.delete()
        messages.success(request, f"La unidad '{item.nombre}' ha sido eliminada.")
    except ProtectedError:
        messages.error(request, f"La unidad '{item.nombre}' no se puede eliminar porque está en uso.")
    return redirect('inventario:unidad_presentacion_list')

@login_required
@require_GET
def productos_api(request):
    search = (request.GET.get('search') or '').strip()

    user = request.user
    sucursal = getattr(user, 'sucursal', None)

    productos = Producto.objects.select_related(
        'categoria',
        'laboratorio',
        'forma_farmaceutica',
        'unidad_venta'
    ).all()

    if search:
        productos = productos.filter(
            Q(nombre__icontains=search) |
            Q(codigo_barras__icontains=search) |
            Q(concentracion__icontains=search) |
            Q(laboratorio__nombre__icontains=search) |
            Q(categoria__nombre__icontains=search)
        )

    productos = productos.order_by('nombre')[:40]

    results = []

    for producto in productos:
        stock_qs = StockProducto.objects.filter(
            producto=producto,
            cantidad__gt=0
        )

        if sucursal:
            stock_qs = stock_qs.filter(sucursal=sucursal)

        stock_total = stock_qs.aggregate(
            total=Sum('cantidad')
        )['total'] or Decimal('0.00')

        precio_venta = producto.precio_venta_sugerido or Decimal('0.00')

        results.append({
            'id': producto.id,
            'nombre': producto.nombre,
            'descripcion': producto.descripcion or '',
            'codigo_barras': producto.codigo_barras or '',
            'concentracion': producto.concentracion or '',
            'precio_venta': str(precio_venta),
            'stock_total': str(stock_total),
            'imagen_producto': producto.imagen_producto.url if producto.imagen_producto else '',
            'laboratorio_nombre': producto.laboratorio.nombre if producto.laboratorio else '',
            'categoria_nombre': producto.categoria.nombre if producto.categoria else '',
            'forma_farmaceutica': producto.forma_farmaceutica.nombre if producto.forma_farmaceutica else '',
            'unidad_venta': producto.unidad_venta.nombre if producto.unidad_venta else 'UNIDAD',
        })

    return JsonResponse({
        'results': results
    })
    
@login_required
@require_GET
def buscar_stock_api(request):
    sucursal_id = request.GET.get('sucursal_id')
    search = request.GET.get('search', '').strip()

    if not sucursal_id:
        return JsonResponse({
            'error': 'Debe enviar una sucursal.'
        }, status=400)

    stock = StockProducto.objects.select_related(
        'producto',
        'sucursal'
    ).filter(
        sucursal_id=sucursal_id,
        cantidad__gt=0
    )

    if search:
        stock = stock.filter(
            producto__nombre__icontains=search
        )

    stock = stock.order_by('producto__nombre')[:20]

    results = []

    for item in stock:
        results.append({
            'id': item.id,
            'producto': item.producto_id,
            'producto_id': item.producto_id,
            'producto_nombre': item.producto.nombre,
            'sucursal': item.sucursal_id,
            'lote': item.lote or '',
            'cantidad': item.cantidad,
            'fecha_vencimiento': item.fecha_vencimiento.strftime('%d/%m/%Y') if item.fecha_vencimiento else '',
            'precio_compra': str(item.precio_compra) if item.precio_compra else '0.00',
            'precio_venta': str(item.precio_venta) if item.precio_venta else '0.00',
        })

    return JsonResponse({
        'results': results
    })