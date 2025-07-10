# clientes/views.py

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Cliente
from core.models import Farmacia

@login_required
def clientes_home_view(request):
    """
    Muestra la página principal con el listado de clientes.
    """
    return render(request, 'clientes_templates/clientes_home.html')

@login_required
def cliente_form_view(request, pk=None):
    """
    Muestra el formulario para CREAR o EDITAR un cliente.
    """
    context = {
        'cliente': None,
        'farmacias': Farmacia.objects.filter(activo=True).order_by('nombre'),
        # --- AÑADE ESTA LÍNEA ---
        'tipos_documento': Cliente.TIPO_DOCUMENTO_CHOICES,
    }
    if pk:
        context['cliente'] = get_object_or_404(Cliente, pk=pk)
        
    return render(request, 'clientes_templates/cliente_form.html', context)