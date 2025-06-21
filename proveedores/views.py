# proveedores/views.py
from django.shortcuts import render
from django.http import HttpResponse

def proveedores_home_view(request):
    """
    Vista de ejemplo para la página de inicio de la aplicación de proveedores.
    Aquí podríamos listar proveedores o mostrar un resumen.
    """
    return HttpResponse("<h1>Gestión de Proveedores</h1><p>Esta es la página de inicio de la aplicación de proveedores. Aquí podrás ver, añadir y gestionar a los proveedores de la farmacia.</p>")

# Puedes añadir más vistas aquí para listar proveedores, ver detalles de un proveedor, etc.
# from .models import Proveedor
# from django.views.generic import ListView, DetailView

# class ProveedorListView(ListView):
#     model = Proveedor
#     template_name = 'proveedores/proveedor_list.html'
#     context_object_name = 'proveedores'
#     paginate_by = 10

# class ProveedorDetailView(DetailView):
#     model = Proveedor
#     template_name = 'proveedores/proveedor_detail.html'
#     context_object_name = 'proveedor'
