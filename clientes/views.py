# clientes/views.py
from django.shortcuts import render
from django.http import HttpResponse

def clientes_home_view(request):
    """
    Vista de ejemplo para la página de inicio de la aplicación de clientes.
    Más adelante, aquí se podría listar clientes, añadir formularios, etc.
    """
    return HttpResponse("<h1>Gestión de Clientes</h1><p>Esta es la página de inicio de la aplicación de clientes. Aquí podrás ver, añadir y gestionar a los clientes.</p>")

# Puedes añadir más vistas aquí para listar clientes, ver detalles de un cliente, etc.
# from .models import Cliente
# from django.views.generic import ListView, DetailView

# class ClienteListView(ListView):
#     model = Cliente
#     template_name = 'clientes/cliente_list.html' # Asegúrate de crear este template
#     context_object_name = 'clientes'
#     paginate_by = 10

# class ClienteDetailView(DetailView):
#     model = Cliente
#     template_name = 'clientes/cliente_detail.html' # Asegúrate de crear este template
#     context_object_name = 'cliente'
