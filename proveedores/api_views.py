# proveedores/api_views.py

from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Proveedor
from .serializers import ProveedorSerializer
from core.permissions import IsAdminOrManager # <-- ¡Aquí se importa!

class ProveedorViewSet(viewsets.ModelViewSet):
    """
    API endpoint que permite a los Proveedores ser vistos o editados.
    Solo administradores y gerentes de sucursal pueden gestionar proveedores.
    """
    queryset = Proveedor.objects.all().order_by('nombre_comercial')
    serializer_class = ProveedorSerializer
    permission_classes = [IsAdminOrManager] # <-- ¡Aquí se aplica!
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['activo', 'tipo_documento']
    search_fields = [
        'nombre_comercial', 'razon_social', 'numero_documento',
        'persona_contacto', 'email', 'telefono'
    ]
    ordering_fields = ['nombre_comercial', 'razon_social', 'fecha_registro', 'activo']

    def get_queryset(self):
        return super().get_queryset()
