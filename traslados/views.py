# traslados/views.py
from django.shortcuts import render
from django.http import HttpResponse

def traslados_home_view(request):
    """
    Vista de ejemplo para la página de inicio de la aplicación de traslados.
    Aquí podríamos listar las transferencias pendientes o realizadas.
    """
    return HttpResponse("<h1>Gestión de Traslados de Stock</h1><p>Esta es la página de inicio de la aplicación de traslados. Aquí podrás gestionar los movimientos de stock entre sucursales.</p>")

# Más adelante, aquí irán las vistas para crear una transferencia,
# listar transferencias, confirmar envíos/recepciones, etc.
