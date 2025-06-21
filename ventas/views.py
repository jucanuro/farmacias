# ventas/views.py
from django.shortcuts import render
from django.http import HttpResponse

def ventas_home_view(request):
    """
    Vista de ejemplo para la página de inicio de la aplicación de ventas.
    Aquí se podría mostrar un resumen de ventas recientes o un punto de venta (POS).
    """
    return HttpResponse("<h1>Gestión de Ventas</h1><p>Esta es la página de inicio de la aplicación de ventas. Aquí podrás registrar y consultar todas las transacciones de venta.</p>")

# Más adelante, aquí irán las vistas para el Punto de Venta (POS),
# listado de ventas, detalles de venta, etc.
