from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import Sum, Subquery, OuterRef, IntegerField
from django.db.models.functions import Coalesce
from django.db.models import ProtectedError
from .models import CategoriaProducto, Laboratorio,FormaFarmaceutica, PrincipioActivo, Producto, StockProducto, Sucursal, MovimientoInventario,UnidadPresentacion
from .forms import CategoriaProductoForm, LaboratorioForm, FormaFarmaceuticaForm, PrincipioActivoForm, ProductoForm,StockEntradaForm, UnidadPresentacionForm

def inventario_home_view(request):
    return HttpResponse("<h1>Gestión de Inventario</h1><p>Esta es la página de inicio de la aplicación de inventario. Aquí podrás ver y gestionar productos y stock.</p>")

def categoria_list_view(request):
    lista_de_categorias = CategoriaProducto.objects.all().order_by('nombre')
    context = {
        'categorias': lista_de_categorias,
    }
    return render(request, 'inventario_templates/categoria_list.html', context)

def categoria_create_view(request):
    if request.method == 'POST':
        form = CategoriaProductoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'La categoría ha sido creada con éxito.')
            return redirect('inventario:categoria_list')
    else:
        form = CategoriaProductoForm()
    
    context = {
        'form': form
    }
    return render(request, 'inventario_templates/categoria_form.html', context)

def categoria_update_view(request, pk):
    categoria = get_object_or_404(CategoriaProducto, pk=pk)
    if request.method == 'POST':
        form = CategoriaProductoForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, f"La categoría '{categoria.nombre}' ha sido actualizada con éxito.")
            return redirect('inventario:categoria_list')
    else:
        form = CategoriaProductoForm(instance=categoria)
    
    context = {
        'form': form,
        'categoria': categoria
    }
    return render(request, 'inventario_templates/categoria_form.html', context)

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
    context = {
        'laboratorios': lista_de_laboratorios
    }
    return render(request, 'inventario_templates/laboratorio_list.html', context)

def laboratorio_create_view(request):
    if request.method == 'POST':
        form = LaboratorioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'El laboratorio ha sido creado con éxito.')
            return redirect('inventario:laboratorio_list')
    else:
        form = LaboratorioForm()
    context = {'form': form}
    return render(request, 'inventario_templates/laboratorio_form.html', context)


def laboratorio_update_view(request, pk):
    laboratorio = get_object_or_404(Laboratorio, pk=pk)
    if request.method == 'POST':
        form = LaboratorioForm(request.POST, instance=laboratorio)
        if form.is_valid():
            form.save()
            messages.success(request, f"El laboratorio '{laboratorio.nombre}' ha sido actualizado con éxito.")
            return redirect('inventario:laboratorio_list')
    else:
        form = LaboratorioForm(instance=laboratorio)
    
    context = {
        'form': form,
        'laboratorio': laboratorio
    }
    return render(request, 'inventario_templates/laboratorio_form.html', context)

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
    context = {'formas_farmaceuticas': lista}
    return render(request, 'inventario_templates/forma_farmaceutica_list.html', context)

def forma_farmaceutica_create_view(request):
    if request.method == 'POST':
        form = FormaFarmaceuticaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'La forma farmacéutica ha sido creada con éxito.')
            return redirect('inventario:forma_farmaceutica_list')
    else:
        form = FormaFarmaceuticaForm()
    context = {'form': form}
    return render(request, 'inventario_templates/forma_farmaceutica_form.html', context)

def forma_farmaceutica_update_view(request, pk):
    item = get_object_or_404(FormaFarmaceutica, pk=pk)
    if request.method == 'POST':
        form = FormaFarmaceuticaForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, f"La forma farmacéutica '{item.nombre}' ha sido actualizada con éxito.")
            return redirect('inventario:forma_farmaceutica_list')
    else:
        form = FormaFarmaceuticaForm(instance=item)
    context = {'form': form, 'forma_farmaceutica': item}
    return render(request, 'inventario_templates/forma_farmaceutica_form.html', context)

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
    context = {'principios_activos': lista}
    return render(request, 'inventario_templates/principio_activo_list.html', context)

def principio_activo_create_view(request):
    if request.method == 'POST':
        form = PrincipioActivoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'El principio activo ha sido creado con éxito.')
            return redirect('inventario:principio_activo_list')
    else:
        form = PrincipioActivoForm()
    context = {'form': form}
    return render(request, 'inventario_templates/principio_activo_form.html', context)

def principio_activo_update_view(request, pk):
    item = get_object_or_404(PrincipioActivo, pk=pk)
    if request.method == 'POST':
        form = PrincipioActivoForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, f"El principio activo '{item.nombre}' ha sido actualizado con éxito.")
            return redirect('inventario:principio_activo_list')
    else:
        form = PrincipioActivoForm(instance=item)
    context = {'form': form, 'principio_activo': item}
    return render(request, 'inventario_templates/principio_activo_form.html', context)

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

    # Definimos la subconsulta base que busca por producto
    stock_subquery = StockProducto.objects.filter(producto=OuterRef('pk'))

    user = request.user
   
    if hasattr(user, 'rol') and user.rol and user.rol.nombre == 'Gerente de Sucursal' and hasattr(user, 'sucursal') and user.sucursal:
        stock_subquery = stock_subquery.filter(sucursal=user.sucursal)
  
    stock_total_subquery = stock_subquery.values('producto').annotate(
        total_stock=Sum('cantidad')
    ).values('total_stock')

    lista_productos = Producto.objects.select_related(
        'categoria', 'laboratorio'
    ).annotate(
        stock_sucursal=Coalesce(
            Subquery(stock_total_subquery, output_field=IntegerField()),
            0
        )
    ).order_by('nombre')
    
    context = {
        'productos': lista_productos
    }
    return render(request, 'inventario_templates/producto_list.html', context)

def producto_create_view(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'El producto ha sido creado con éxito.')
            return redirect('inventario:producto_list')
        else:
            print(form.errors.as_json()) 

    else:
        form = ProductoForm()
    context = {'form': form}
    return render(request, 'inventario_templates/producto_form.html', context)


def producto_update_view(request, pk):
    # Obtenemos el producto que se va a editar
    producto = get_object_or_404(Producto, pk=pk)

    # Si la petición es POST, significa que el usuario ha enviado el formulario
    if request.method == 'POST':
        # Creamos el formulario con los datos enviados Y con la instancia del producto a editar
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            # Si los datos son válidos, guardamos y redirigimos
            form.save()
            messages.success(request, f"El producto '{producto.nombre}' ha sido actualizado con éxito.")
            return redirect('inventario:producto_list')
        # Si el formulario NO es válido, la función continúa y renderiza la plantilla de abajo,
        # mostrando el formulario con los errores.
    else:
        # Si la petición es GET (la primera vez que se carga la página),
        # creamos el formulario con los datos iniciales del producto.
        form = ProductoForm(instance=producto)

    # El contexto se prepara aquí, tanto para el GET inicial como para los POST con errores.
    context = {
        'form': form,
        'producto': producto
    }
    return render(request, 'inventario_templates/producto_form.html', context)


def producto_detail_view(request, pk):
    """
    Muestra los detalles de un producto, su stock actual por sucursal,
    y procesa el formulario para añadir nuevo stock.
    """
    producto = get_object_or_404(Producto, pk=pk)

    # Lógica para procesar el formulario de añadir stock
    if request.method == 'POST':
        # Aseguramos que el formulario se procese solo si viene del botón correcto
        # (en caso de que añadas más formularios a esta página en el futuro)
        stock_form = StockEntradaForm(request.POST)
        if stock_form.is_valid():
            datos = stock_form.cleaned_data
            
            # Buscamos si ya existe un stock con el mismo lote en la misma sucursal
            stock, created = StockProducto.objects.get_or_create(
                producto=producto,
                sucursal=datos['sucursal'],
                lote=datos['lote'],
                defaults={
                    'fecha_vencimiento': datos['fecha_vencimiento'],
                    'precio_compra': datos['precio_compra'],
                    'precio_venta': datos['precio_venta'] # <-- CORRECCIÓN: Se añade el precio de venta
                }
            )
            
            # Si el lote ya existía, actualizamos sus datos y sumamos la cantidad
            if not created:
                stock.cantidad += datos['cantidad']
                # Opcional: decidir si se actualiza el precio con cada nueva compra del mismo lote
                stock.precio_compra = datos['precio_compra']
                stock.precio_venta = datos['precio_venta']
                stock.fecha_vencimiento = datos['fecha_vencimiento']
            else:
                # Si es un lote nuevo, la cantidad es la del formulario
                stock.cantidad = datos['cantidad']

            stock.ubicacion_almacen = datos['ubicacion_almacen']
            stock.save()

            # Creamos el movimiento de inventario para registrar la entrada
            MovimientoInventario.objects.create(
                producto=producto,
                sucursal=datos['sucursal'],
                stock_afectado=stock,
                tipo_movimiento='ENTRADA',
                cantidad=datos['cantidad'],
                usuario=request.user,
                referencia_doc=f"Compra Lote {datos['lote']}"
            )
            
            messages.success(request, f"Se ha añadido stock para '{producto.nombre}' con éxito.")
            # Redirigimos a la misma página para ver el resultado
            return redirect('inventario:producto_detail', pk=producto.pk)
    else:
        # Si la petición es GET, mostramos un formulario vacío
        stock_form = StockEntradaForm()
        
    # Obtenemos el stock existente para mostrarlo en la tabla
    stock_items = StockProducto.objects.filter(producto=producto).select_related('sucursal').order_by('sucursal__nombre', 'fecha_vencimiento')

    context = {
        'producto': producto,
        'stock_items': stock_items,
        'stock_form': stock_form # Pasamos el formulario a la plantilla
    }
    return render(request, 'inventario_templates/producto_detail.html', context)     
    

def unidad_presentacion_list_view(request):
    lista = UnidadPresentacion.objects.select_related('padre').all().order_by('nombre')
    context = {'unidades': lista}
    return render(request, 'inventario_templates/unidad_presentacion_list.html', context)

def unidad_presentacion_create_view(request):
    if request.method == 'POST':
        form = UnidadPresentacionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'La unidad de presentación ha sido creada.')
            return redirect('inventario:unidad_presentacion_list')
    else:
        form = UnidadPresentacionForm()
    context = {'form': form}
    return render(request, 'inventario_templates/unidad_presentacion_form.html', context)

def unidad_presentacion_update_view(request, pk):
    item = get_object_or_404(UnidadPresentacion, pk=pk)
    if request.method == 'POST':
        form = UnidadPresentacionForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, f"La unidad '{item.nombre}' ha sido actualizada.")
            return redirect('inventario:unidad_presentacion_list')
    else:
        form = UnidadPresentacionForm(instance=item)
    context = {'form': form, 'unidad': item}
    return render(request, 'inventario_templates/unidad_presentacion_form.html', context)

@require_POST
def unidad_presentacion_delete_view(request, pk):
    item = get_object_or_404(UnidadPresentacion, pk=pk)
    try:
        item.delete()
        messages.success(request, f"La unidad '{item.nombre}' ha sido eliminada.")
    except ProtectedError:
        messages.error(request, f"La unidad '{item.nombre}' no se puede eliminar porque está en uso.")
    return redirect('inventario:unidad_presentacion_list')