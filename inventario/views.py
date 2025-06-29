from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import CategoriaProducto
from .forms import CategoriaProductoForm

def inventario_home_view(request):
    return HttpResponse("<h1>Gestión de Inventario</h1><p>Esta es la página de inicio de la aplicación de inventario. Aquí podrás ver y gestionar productos y stock.</p>")

def categoria_list_view(request):
    lista_de_categorias = CategoriaProducto.objects.all().order_by('nombre')
    context = {
        'categorias': lista_de_categorias
    }
    return render(request, 'inventario_templates/categoria_list.html', context)

def categoria_create_view(request):
    if request.method == 'POST':
        form = CategoriaProductoForm(request.POST)
        if form.is_valid():
            form.save()
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
            return redirect('inventario:categoria_list')
    else:
        form = CategoriaProductoForm(instance=categoria)
    
    context = {
        'form': form,
        'categoria': categoria
    }
    return render(request, 'inventario_templates/categoria_form.html', context)