from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import IntegrityError, transaction
from django.db.models import Sum, Subquery, OuterRef, IntegerField, Q
from django.db.models.deletion import ProtectedError
from django.db.models.functions import Coalesce
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_GET, require_POST

from core.models import Sucursal
from .models import (
    CategoriaProducto,
    Laboratorio,
    FormaFarmaceutica,
    PrincipioActivo,
    Producto,
    StockProducto,
    MovimientoInventario,
    UnidadPresentacion,
    PrecioProductoSucursal,
)


def _to_decimal(value, default="0.00"):
    try:
        return Decimal(str(value or default))
    except (InvalidOperation, TypeError, ValueError):
        return Decimal(default)


def _to_int(value, default=0):
    try:
        return int(value or default)
    except (TypeError, ValueError):
        return default


def inventario_home_view(request):
    return HttpResponse(
        "<h1>Gestión de Inventario</h1>"
        "<p>Gestiona productos, stock por sucursal, precios por sucursal y movimientos.</p>"
    )


def categoria_list_view(request):
    categorias = CategoriaProducto.objects.all().order_by("nombre")
    return render(request, "inventario_templates/categoria_list.html", {
        "categorias": categorias
    })


def categoria_create_view(request):
    if request.method == "POST":
        nombre = (request.POST.get("nombre") or "").strip()
        descripcion = (request.POST.get("descripcion") or "").strip()

        if not nombre:
            messages.error(request, "El nombre de la categoría es obligatorio.")
            return redirect("inventario:categoria_create")

        try:
            CategoriaProducto.objects.create(
                nombre=nombre,
                descripcion=descripcion
            )
            messages.success(request, "La categoría ha sido creada con éxito.")
            return redirect("inventario:categoria_list")
        except IntegrityError:
            messages.error(request, "Ya existe una categoría con ese nombre.")

    return render(request, "inventario_templates/categoria_form.html")


def categoria_update_view(request, pk):
    categoria = get_object_or_404(CategoriaProducto, pk=pk)

    if request.method == "POST":
        nombre = (request.POST.get("nombre") or "").strip()
        descripcion = (request.POST.get("descripcion") or "").strip()

        if not nombre:
            messages.error(request, "El nombre de la categoría es obligatorio.")
            return redirect("inventario:categoria_update", pk=pk)

        categoria.nombre = nombre
        categoria.descripcion = descripcion

        try:
            categoria.save()
            messages.success(request, f"La categoría '{categoria.nombre}' ha sido actualizada.")
            return redirect("inventario:categoria_list")
        except IntegrityError:
            messages.error(request, "Ya existe una categoría con ese nombre.")

    return render(request, "inventario_templates/categoria_form.html", {
        "categoria": categoria
    })


@require_POST
def categoria_delete_view(request, pk):
    categoria = get_object_or_404(CategoriaProducto, pk=pk)

    try:
        categoria.delete()
        messages.success(request, f"La categoría '{categoria.nombre}' ha sido eliminada.")
    except ProtectedError:
        messages.error(request, f"La categoría '{categoria.nombre}' no se puede eliminar porque tiene productos asociados.")

    return redirect("inventario:categoria_list")


def laboratorio_list_view(request):
    laboratorios = Laboratorio.objects.all().order_by("nombre")
    return render(request, "inventario_templates/laboratorio_list.html", {
        "laboratorios": laboratorios
    })


def laboratorio_create_view(request):
    if request.method == "POST":
        nombre = (request.POST.get("nombre") or "").strip()
        direccion = (request.POST.get("direccion") or "").strip()
        telefono = (request.POST.get("telefono") or "").strip()
        email = (request.POST.get("email") or "").strip()

        if not nombre:
            messages.error(request, "El nombre del laboratorio es obligatorio.")
            return redirect("inventario:laboratorio_create")

        try:
            Laboratorio.objects.create(
                nombre=nombre,
                direccion=direccion,
                telefono=telefono,
                email=email
            )
            messages.success(request, "El laboratorio ha sido creado con éxito.")
            return redirect("inventario:laboratorio_list")
        except IntegrityError:
            messages.error(request, "Ya existe un laboratorio con ese nombre.")

    return render(request, "inventario_templates/laboratorio_form.html")


def laboratorio_update_view(request, pk):
    laboratorio = get_object_or_404(Laboratorio, pk=pk)

    if request.method == "POST":
        laboratorio.nombre = (request.POST.get("nombre") or "").strip()
        laboratorio.direccion = (request.POST.get("direccion") or "").strip()
        laboratorio.telefono = (request.POST.get("telefono") or "").strip()
        laboratorio.email = (request.POST.get("email") or "").strip()

        if not laboratorio.nombre:
            messages.error(request, "El nombre del laboratorio es obligatorio.")
            return redirect("inventario:laboratorio_update", pk=pk)

        try:
            laboratorio.save()
            messages.success(request, f"El laboratorio '{laboratorio.nombre}' ha sido actualizado.")
            return redirect("inventario:laboratorio_list")
        except IntegrityError:
            messages.error(request, "Ya existe un laboratorio con ese nombre.")

    return render(request, "inventario_templates/laboratorio_form.html", {
        "laboratorio": laboratorio
    })


@require_POST
def laboratorio_delete_view(request, pk):
    laboratorio = get_object_or_404(Laboratorio, pk=pk)

    try:
        laboratorio.delete()
        messages.success(request, f"El laboratorio '{laboratorio.nombre}' ha sido eliminado.")
    except ProtectedError:
        messages.error(request, f"El laboratorio '{laboratorio.nombre}' no se puede eliminar porque tiene productos asociados.")

    return redirect("inventario:laboratorio_list")


def forma_farmaceutica_list_view(request):
    formas = FormaFarmaceutica.objects.all().order_by("nombre")
    return render(request, "inventario_templates/forma_farmaceutica_list.html", {
        "formas_farmaceuticas": formas
    })


def forma_farmaceutica_create_view(request):
    if request.method == "POST":
        nombre = (request.POST.get("nombre") or "").strip()
        descripcion = (request.POST.get("descripcion") or "").strip()

        if not nombre:
            messages.error(request, "El nombre de la forma farmacéutica es obligatorio.")
            return redirect("inventario:forma_farmaceutica_create")

        try:
            FormaFarmaceutica.objects.create(
                nombre=nombre,
                descripcion=descripcion
            )
            messages.success(request, "La forma farmacéutica ha sido creada.")
            return redirect("inventario:forma_farmaceutica_list")
        except IntegrityError:
            messages.error(request, "Ya existe una forma farmacéutica con ese nombre.")

    return render(request, "inventario_templates/forma_farmaceutica_form.html")


def forma_farmaceutica_update_view(request, pk):
    item = get_object_or_404(FormaFarmaceutica, pk=pk)

    if request.method == "POST":
        item.nombre = (request.POST.get("nombre") or "").strip()
        item.descripcion = (request.POST.get("descripcion") or "").strip()

        if not item.nombre:
            messages.error(request, "El nombre de la forma farmacéutica es obligatorio.")
            return redirect("inventario:forma_farmaceutica_update", pk=pk)

        try:
            item.save()
            messages.success(request, f"La forma farmacéutica '{item.nombre}' ha sido actualizada.")
            return redirect("inventario:forma_farmaceutica_list")
        except IntegrityError:
            messages.error(request, "Ya existe una forma farmacéutica con ese nombre.")

    return render(request, "inventario_templates/forma_farmaceutica_form.html", {
        "forma_farmaceutica": item
    })


@require_POST
def forma_farmaceutica_delete_view(request, pk):
    item = get_object_or_404(FormaFarmaceutica, pk=pk)

    try:
        item.delete()
        messages.success(request, f"La forma farmacéutica '{item.nombre}' ha sido eliminada.")
    except ProtectedError:
        messages.error(request, f"La forma farmacéutica '{item.nombre}' no se puede eliminar porque tiene productos asociados.")

    return redirect("inventario:forma_farmaceutica_list")


def principio_activo_list_view(request):
    principios = PrincipioActivo.objects.all().order_by("nombre")
    return render(request, "inventario_templates/principio_activo_list.html", {
        "principios_activos": principios
    })


def principio_activo_create_view(request):
    if request.method == "POST":
        nombre = (request.POST.get("nombre") or "").strip()
        descripcion = (request.POST.get("descripcion") or "").strip()

        if not nombre:
            messages.error(request, "El nombre del principio activo es obligatorio.")
            return redirect("inventario:principio_activo_create")

        try:
            PrincipioActivo.objects.create(
                nombre=nombre,
                descripcion=descripcion
            )
            messages.success(request, "El principio activo ha sido creado.")
            return redirect("inventario:principio_activo_list")
        except IntegrityError:
            messages.error(request, "Ya existe un principio activo con ese nombre.")

    return render(request, "inventario_templates/principio_activo_form.html")


def principio_activo_update_view(request, pk):
    item = get_object_or_404(PrincipioActivo, pk=pk)

    if request.method == "POST":
        item.nombre = (request.POST.get("nombre") or "").strip()
        item.descripcion = (request.POST.get("descripcion") or "").strip()

        if not item.nombre:
            messages.error(request, "El nombre del principio activo es obligatorio.")
            return redirect("inventario:principio_activo_update", pk=pk)

        try:
            item.save()
            messages.success(request, f"El principio activo '{item.nombre}' ha sido actualizado.")
            return redirect("inventario:principio_activo_list")
        except IntegrityError:
            messages.error(request, "Ya existe un principio activo con ese nombre.")

    return render(request, "inventario_templates/principio_activo_form.html", {
        "principio_activo": item
    })


@require_POST
def principio_activo_delete_view(request, pk):
    item = get_object_or_404(PrincipioActivo, pk=pk)

    try:
        item.delete()
        messages.success(request, f"El principio activo '{item.nombre}' ha sido eliminado.")
    except ProtectedError:
        messages.error(request, f"El principio activo '{item.nombre}' no se puede eliminar porque tiene productos asociados.")

    return redirect("inventario:principio_activo_list")


def unidad_presentacion_list_view(request):
    unidades = UnidadPresentacion.objects.select_related("padre").all().order_by("nombre")
    return render(request, "inventario_templates/unidad_presentacion_list.html", {
        "unidades": unidades
    })


def unidad_presentacion_create_view(request):
    if request.method == "POST":
        nombre = (request.POST.get("nombre") or "").strip()
        padre_id = request.POST.get("padre") or None
        factor_conversion = _to_int(request.POST.get("factor_conversion"), 1)

        if not nombre:
            messages.error(request, "El nombre de la unidad es obligatorio.")
            return redirect("inventario:unidad_presentacion_create")

        if factor_conversion < 1:
            messages.error(request, "El factor de conversión debe ser mayor o igual a 1.")
            return redirect("inventario:unidad_presentacion_create")

        try:
            UnidadPresentacion.objects.create(
                nombre=nombre,
                padre_id=padre_id,
                factor_conversion=factor_conversion
            )
            messages.success(request, "La unidad de presentación ha sido creada.")
            return redirect("inventario:unidad_presentacion_list")
        except IntegrityError:
            messages.error(request, "Ya existe una unidad con ese nombre.")

    return render(request, "inventario_templates/unidad_presentacion_form.html", {
        "unidades_padre": UnidadPresentacion.objects.all().order_by("nombre")
    })


def unidad_presentacion_update_view(request, pk):
    item = get_object_or_404(UnidadPresentacion, pk=pk)

    if request.method == "POST":
        nombre = (request.POST.get("nombre") or "").strip()
        padre_id = request.POST.get("padre") or None
        factor_conversion = _to_int(request.POST.get("factor_conversion"), 1)

        if not nombre:
            messages.error(request, "El nombre de la unidad es obligatorio.")
            return redirect("inventario:unidad_presentacion_update", pk=pk)

        if str(padre_id) == str(item.pk):
            messages.error(request, "Una unidad no puede ser padre de sí misma.")
            return redirect("inventario:unidad_presentacion_update", pk=pk)

        if factor_conversion < 1:
            messages.error(request, "El factor de conversión debe ser mayor o igual a 1.")
            return redirect("inventario:unidad_presentacion_update", pk=pk)

        item.nombre = nombre
        item.padre_id = padre_id
        item.factor_conversion = factor_conversion

        try:
            item.save()
            messages.success(request, f"La unidad '{item.nombre}' ha sido actualizada.")
            return redirect("inventario:unidad_presentacion_list")
        except IntegrityError:
            messages.error(request, "Ya existe una unidad con ese nombre.")

    return render(request, "inventario_templates/unidad_presentacion_form.html", {
        "unidad": item,
        "unidades_padre": UnidadPresentacion.objects.exclude(pk=pk).order_by("nombre")
    })


@require_POST
def unidad_presentacion_delete_view(request, pk):
    item = get_object_or_404(UnidadPresentacion, pk=pk)

    try:
        item.delete()
        messages.success(request, f"La unidad '{item.nombre}' ha sido eliminada.")
    except ProtectedError:
        messages.error(request, f"La unidad '{item.nombre}' no se puede eliminar porque está en uso.")

    return redirect("inventario:unidad_presentacion_list")


def producto_list_view(request):
    stock_subquery = StockProducto.objects.filter(
        producto=OuterRef("pk"),
        activo=True,
    )

    user_sucursal = getattr(request.user, "sucursal", None)

    if user_sucursal:
        stock_subquery = stock_subquery.filter(sucursal=user_sucursal)

    stock_total_subquery = stock_subquery.values("producto").annotate(
        total_stock=Sum("cantidad_disponible")
    ).values("total_stock")

    productos = Producto.objects.select_related(
        "categoria",
        "laboratorio",
        "forma_farmaceutica",
        "unidad_venta",
    ).annotate(
        stock_sucursal=Coalesce(
            Subquery(stock_total_subquery, output_field=IntegerField()),
            0
        )
    ).order_by("nombre")

    return render(request, "inventario_templates/producto_list.html", {
        "productos": productos
    })


def producto_form_view(request, pk=None):
    producto = get_object_or_404(Producto, pk=pk) if pk else None

    categorias = CategoriaProducto.objects.all().order_by("nombre")
    laboratorios = Laboratorio.objects.all().order_by("nombre")
    principios = PrincipioActivo.objects.all().order_by("nombre")
    formas = FormaFarmaceutica.objects.all().order_by("nombre")
    unidades = UnidadPresentacion.objects.all().order_by("nombre")

    if request.method == "POST":
        nombre = (request.POST.get("nombre") or "").strip()
        sku = (request.POST.get("sku") or "").strip() or None
        descripcion = (request.POST.get("descripcion") or "").strip()
        codigo_barras = (request.POST.get("codigo_barras") or "").strip() or None
        concentracion = (request.POST.get("concentracion") or "").strip()

        categoria_id = request.POST.get("categoria") or None
        laboratorio_id = request.POST.get("laboratorio") or None
        principio_activo_id = request.POST.get("principio_activo") or None
        forma_farmaceutica_id = request.POST.get("forma_farmaceutica") or None
        unidad_compra_id = request.POST.get("unidad_compra") or None
        unidad_venta_id = request.POST.get("unidad_venta") or None

        precio_venta_sugerido = _to_decimal(request.POST.get("precio_venta_sugerido"), "0.00")
        margen_ganancia_sugerido = _to_decimal(request.POST.get("margen_ganancia_sugerido"), "20.00")

        tipo_igv = request.POST.get("tipo_igv") or "10"
        precio_incluye_igv = request.POST.get("precio_incluye_igv") == "on"

        unidades_por_caja = _to_int(request.POST.get("unidades_por_caja"), 1)
        unidades_por_blister = _to_int(request.POST.get("unidades_por_blister"), 1)

        aplica_receta = request.POST.get("aplica_receta") == "on"
        es_controlado = request.POST.get("es_controlado") == "on"
        activo = request.POST.get("activo") == "on" if pk else True

        errores = []

        if not nombre:
            errores.append("El nombre del producto es obligatorio.")

        if not categoria_id:
            errores.append("La categoría es obligatoria.")

        if not laboratorio_id:
            errores.append("El laboratorio es obligatorio.")

        if not forma_farmaceutica_id:
            errores.append("La forma farmacéutica es obligatoria.")

        if unidades_por_caja < 1:
            errores.append("Las unidades por caja deben ser mayores o iguales a 1.")

        if unidades_por_blister < 1:
            errores.append("Las unidades por blíster deben ser mayores o iguales a 1.")

        if errores:
            for error in errores:
                messages.error(request, error)
        else:
            try:
                if producto is None:
                    producto = Producto()

                producto.nombre = nombre
                producto.sku = sku
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
                producto.tipo_igv = tipo_igv
                producto.precio_incluye_igv = precio_incluye_igv
                producto.unidades_por_caja = unidades_por_caja
                producto.unidades_por_blister = unidades_por_blister
                producto.aplica_receta = aplica_receta
                producto.es_controlado = es_controlado
                producto.activo = activo

                if request.FILES.get("imagen_producto"):
                    producto.imagen_producto = request.FILES.get("imagen_producto")

                producto.save()

                if pk:
                    messages.success(request, f"El producto '{producto.nombre}' ha sido actualizado.")
                else:
                    messages.success(request, f"El producto '{producto.nombre}' ha sido creado.")

                return redirect("inventario:producto_list")

            except IntegrityError:
                messages.error(request, "Ya existe un producto con ese SKU o código de barras.")

    return render(request, "inventario_templates/producto_form.html", {
        "producto": producto,
        "categorias": categorias,
        "laboratorios": laboratorios,
        "principios": principios,
        "formas": formas,
        "unidades": unidades,
    })


@login_required
@transaction.atomic
def producto_detail_view(request, pk):
    producto = get_object_or_404(Producto, pk=pk)

    if request.method == "POST":
        sucursal_id = request.POST.get("sucursal") or None
        lote = (request.POST.get("lote") or "").strip()
        fecha_vencimiento = request.POST.get("fecha_vencimiento") or None
        cantidad = _to_int(request.POST.get("cantidad"), 0)
        precio_compra = _to_decimal(request.POST.get("precio_compra"), "0.00")
        ubicacion_almacen = (request.POST.get("ubicacion_almacen") or "").strip()

        if not sucursal_id:
            messages.error(request, "Debes seleccionar una sucursal.")
            return redirect("inventario:producto_detail", pk=pk)

        if not lote:
            messages.error(request, "El lote es obligatorio.")
            return redirect("inventario:producto_detail", pk=pk)

        if not fecha_vencimiento:
            messages.error(request, "La fecha de vencimiento es obligatoria.")
            return redirect("inventario:producto_detail", pk=pk)

        if cantidad <= 0:
            messages.error(request, "La cantidad debe ser mayor a cero.")
            return redirect("inventario:producto_detail", pk=pk)

        stock, _ = StockProducto.objects.select_for_update().get_or_create(
            producto=producto,
            sucursal_id=sucursal_id,
            lote=lote,
            defaults={
                "fecha_vencimiento": fecha_vencimiento,
                "cantidad_disponible": 0,
                "cantidad_reservada": 0,
                "precio_compra": precio_compra,
                "ubicacion_almacen": ubicacion_almacen,
                "activo": True,
            }
        )

        cantidad_anterior = stock.cantidad_disponible
        stock.cantidad_disponible += cantidad
        stock.fecha_vencimiento = fecha_vencimiento
        stock.precio_compra = precio_compra
        stock.ubicacion_almacen = ubicacion_almacen
        stock.activo = True
        stock.save()

        MovimientoInventario.objects.create(
            producto=producto,
            sucursal_id=sucursal_id,
            stock_afectado=stock,
            tipo_movimiento="ENTRADA",
            cantidad=cantidad,
            cantidad_anterior=cantidad_anterior,
            cantidad_nueva=stock.cantidad_disponible,
            usuario=request.user,
            referencia_doc=f"ENTRADA-LOTE-{lote}",
            observaciones=f"Entrada manual de stock para lote {lote}"
        )

        messages.success(request, f"Se añadió stock para '{producto.nombre}' correctamente.")
        return redirect("inventario:producto_detail", pk=pk)

    stock_items = StockProducto.objects.filter(
        producto=producto,
        activo=True,
    ).select_related(
        "sucursal"
    ).order_by(
        "fecha_vencimiento"
    )

    paginator = Paginator(stock_items, 6)
    page_number = request.GET.get("page")
    stock_page = paginator.get_page(page_number)

    return render(request, "inventario_templates/producto_detail.html", {
        "producto": producto,
        "stock_items": stock_page,
        "stock_total": stock_items.count(),
        "sucursales": Sucursal.objects.all().order_by("nombre"),
    })


@login_required
@require_GET
def productos_api(request):
    search = (request.GET.get("search") or "").strip()
    sucursal_id = request.GET.get("sucursal_id") or None
    user_sucursal = getattr(request.user, "sucursal", None)

    if not sucursal_id and user_sucursal:
        sucursal_id = user_sucursal.id

    productos = Producto.objects.select_related(
        "categoria",
        "laboratorio",
        "forma_farmaceutica",
        "unidad_venta",
    ).filter(
        activo=True
    )

    if search:
        productos = productos.filter(
            Q(nombre__icontains=search) |
            Q(sku__icontains=search) |
            Q(codigo_barras__icontains=search) |
            Q(concentracion__icontains=search) |
            Q(laboratorio__nombre__icontains=search) |
            Q(categoria__nombre__icontains=search)
        )

    productos = productos.order_by("nombre")[:40]

    results = []

    for producto in productos:
        stock_qs = StockProducto.objects.filter(
            producto=producto,
            activo=True,
            cantidad_disponible__gt=0,
        )

        if sucursal_id:
            stock_qs = stock_qs.filter(sucursal_id=sucursal_id)

        stock_total = stock_qs.aggregate(
            total=Sum("cantidad_disponible")
        )["total"] or 0

        precio_venta = producto.precio_venta_sugerido or Decimal("0.00")

        if sucursal_id:
            precio_sucursal = PrecioProductoSucursal.objects.filter(
                producto=producto,
                sucursal_id=sucursal_id,
                activo=True,
            ).first()

            if precio_sucursal and not precio_sucursal.usa_precio_matriz:
                precio_venta = precio_sucursal.precio_venta

        results.append({
            "id": producto.id,
            "nombre": producto.nombre,
            "sku": producto.sku or "",
            "descripcion": producto.descripcion or "",
            "codigo_barras": producto.codigo_barras or "",
            "concentracion": producto.concentracion or "",
            "precio_venta": str(precio_venta),
            "stock_total": str(stock_total),
            "imagen_producto": producto.imagen_producto.url if producto.imagen_producto else "",
            "laboratorio_nombre": producto.laboratorio.nombre if producto.laboratorio else "",
            "categoria_nombre": producto.categoria.nombre if producto.categoria else "",
            "forma_farmaceutica": producto.forma_farmaceutica.nombre if producto.forma_farmaceutica else "",
            "unidad_venta": producto.unidad_venta.nombre if producto.unidad_venta else "UNIDAD",
        })

    return JsonResponse({
        "results": results
    })


@login_required
@require_GET
def buscar_stock_api(request):
    sucursal_id = request.GET.get("sucursal_id")
    search = (request.GET.get("search") or "").strip()

    if not sucursal_id:
        return JsonResponse({
            "error": "Debe enviar una sucursal."
        }, status=400)

    stock = StockProducto.objects.select_related(
        "producto",
        "producto__categoria",
        "producto__laboratorio",
        "sucursal",
    ).filter(
        sucursal_id=sucursal_id,
        activo=True,
        cantidad_disponible__gt=0,
        producto__activo=True,
    )

    if search:
        stock = stock.filter(
            Q(producto__nombre__icontains=search) |
            Q(producto__sku__icontains=search) |
            Q(producto__codigo_barras__icontains=search) |
            Q(producto__laboratorio__nombre__icontains=search) |
            Q(lote__icontains=search)
        )

    stock = stock.order_by(
        "producto__nombre",
        "fecha_vencimiento"
    )[:20]

    results = []

    for item in stock:
        results.append({
            "id": item.id,
            "producto": item.producto_id,
            "producto_id": item.producto_id,
            "producto_nombre": item.producto.nombre,
            "sku": item.producto.sku or "",
            "codigo_barras": item.producto.codigo_barras or "",
            "laboratorio": item.producto.laboratorio.nombre if item.producto.laboratorio else "",
            "categoria": item.producto.categoria.nombre if item.producto.categoria else "",
            "sucursal": item.sucursal_id,
            "sucursal_nombre": item.sucursal.nombre,
            "lote": item.lote or "",
            "cantidad_disponible": item.cantidad_disponible,
            "cantidad_reservada": item.cantidad_reservada,
            "fecha_vencimiento": item.fecha_vencimiento.strftime("%d/%m/%Y") if item.fecha_vencimiento else "",
            "precio_compra": str(item.precio_compra or Decimal("0.00")),
        })

    return JsonResponse({
        "results": results
    })