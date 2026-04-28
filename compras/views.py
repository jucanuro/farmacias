from django.shortcuts import render, get_object_or_404

from .models import Compra, Proveedor, Sucursal
from .serializers import CompraSerializer


def compras_home_view(request):
    """
    Muestra la página con el listado de compras.
    Los datos se cargarán dinámicamente con JavaScript.
    """
    return render(request, 'compras_templates/compras_home.html')


def compra_create_view(request):
    """
    Prepara y muestra el formulario para registrar una nueva compra.
    """
    proveedores = Proveedor.objects.filter(activo=True).order_by('nombre_comercial')
    sucursales = Sucursal.objects.all().order_by('nombre')

    context = {
        'proveedores': proveedores,
        'sucursales': sucursales,
    }
    return render(request, 'compras_templates/compra_form.html', context)


def compra_edit_view(request, pk):
    """
    Prepara y muestra el formulario para editar una compra existente.
    """
    compra = get_object_or_404(Compra, pk=pk)
    serializer = CompraSerializer(compra)

    proveedores = Proveedor.objects.filter(activo=True).order_by('nombre_comercial')
    sucursales = Sucursal.objects.all().order_by('nombre')

    context = {
        'compra': compra,
        'compra_json': serializer.data,
        'proveedores': proveedores,
        'sucursales': sucursales,
    }
    return render(request, 'compras_templates/compra_form.html', context)
