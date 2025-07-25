# traslados/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from core.models import Sucursal

def traslados_home_view(request):
    # Esta vista ya la tienes
    return render(request, 'traslados_templates/traslados_home.html')

# --- AÑADE ESTA NUEVA VISTA ---
@login_required
def traslado_create_view(request):
    """Renderiza el formulario para crear un nuevo traslado."""
    # Pasamos las sucursales a la plantilla para los menús desplegables
    sucursales = Sucursal.objects.all() 
    context = {
        'sucursales': sucursales
    }
    return render(request, 'traslados_templates/traslado_form.html', context)