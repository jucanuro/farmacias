# ventas/views.py

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def pos_view(request):
    """
    Renderiza la interfaz principal del Punto de Venta (POS).
    Toda la lógica será manejada por JavaScript.
    """
    return render(request, 'ventas_templates/pos.html')

@login_required
def venta_list_view(request):
    """
    Renderiza la página que mostrará el listado de ventas.
    La carga de datos se hará con JavaScript y la API.
    """
    return render(request, 'ventas_templates/venta_list.html')