from django.shortcuts import render
from django.http import HttpResponse

# Importando modelos de OTRAS apps
from proveedores.models import Proveedor
from core.models import Sucursal

# Create your views here.
def compras_home_view(request):
    """
    Vista de ejemplo para la página de inicio de la aplicación de compras.
    """
    return HttpResponse("<h1>Panel Principal de Compras</h1>")

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