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