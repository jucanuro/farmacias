# inventario/views.py
from django.shortcuts import render
from django.http import HttpResponse

def inventario_home_view(request):
    """
    Vista de ejemplo para la página de inicio de la aplicación de inventario.
    Aquí podríamos mostrar un resumen del stock o enlaces a otras secciones.
    """
    return HttpResponse("<h1>Gestión de Inventario</h1><p>Esta es la página de inicio de la aplicación de inventario. Aquí podrás ver y gestionar productos y stock.</p>")

