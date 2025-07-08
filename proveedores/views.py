from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import ProtectedError
from .models import Proveedor
from .forms import ProveedorForm

def proveedor_list_view(request):
    lista = Proveedor.objects.filter(activo=True).order_by('nombre_comercial')
    context = {'proveedores': lista}
    return render(request, 'proveedores_templates/proveedor_list.html', context)

def proveedor_create_view(request):
    if request.method == 'POST':
        form = ProveedorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'El proveedor ha sido creado con éxito.')
            return redirect('proveedores:proveedor_list')
    else:
        form = ProveedorForm()
    context = {'form': form}
    return render(request, 'proveedores_templates/proveedor_form.html', context)

def proveedor_update_view(request, pk):
    item = get_object_or_404(Proveedor, pk=pk)
    if request.method == 'POST':
        form = ProveedorForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, f"El proveedor '{item.nombre_comercial}' ha sido actualizado con éxito.")
            return redirect('proveedores:proveedor_list')
    else:
        form = ProveedorForm(instance=item)
    context = {
        'form': form, 
        'proveedor': item
    }
    return render(request, 'proveedores_templates/proveedor_form.html', context)

@require_POST
def proveedor_delete_view(request, pk):
    item = get_object_or_404(Proveedor, pk=pk)
    try:
        item.delete()
        messages.success(request, f"El proveedor '{item.nombre_comercial}' ha sido eliminado con éxito.")
    except ProtectedError:
        messages.error(request, f"El proveedor '{item.nombre_comercial}' no se puede eliminar porque está asociado a otros registros.")
    
    return redirect('proveedores:proveedor_list')