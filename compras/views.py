# compras/views.py
from django.shortcuts import render
from django.http import HttpResponse

def compras_home_view(request):
    """
    Vista de ejemplo para la página de inicio de la aplicación de compras.
    Aquí podríamos mostrar un resumen de órdenes pendientes, cotizaciones, etc.
    """
    return HttpResponse("<h1>Gestión de Compras</h1><p>Esta es la página de inicio de la aplicación de compras. Aquí podrás gestionar cotizaciones, órdenes de compra y recepciones de productos.</p>")

