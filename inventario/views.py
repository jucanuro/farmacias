from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import ProtectedError
from .models import CategoriaProducto, Laboratorio,FormaFarmaceutica, PrincipioActivo, Producto
from .forms import CategoriaProductoForm, LaboratorioForm, FormaFarmaceuticaForm, PrincipioActivoForm, ProductoForm

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
    lista_productos = Producto.objects.select_related(
        'categoria', 'laboratorio'
    ).all().order_by('nombre')
    
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
        form = ProductoForm()
    context = {'form': form}
    return render(request, 'inventario_templates/producto_form.html', context)


def producto_update_view(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, f"El producto '{producto.nombre}' ha sido actualizado con éxito.")
            return redirect('inventario:producto_list')
    else:
        form = ProductoForm(instance=producto)
    
    context = {
        'form': form,
        'producto': producto
    }
    return render(request, 'inventario_templates/producto_form.html', context)