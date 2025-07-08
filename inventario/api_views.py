from rest_framework import viewsets, permissions, filters
from rest_framework.generics import ListAPIView
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import (
    CategoriaProducto, Laboratorio, PrincipioActivo,
    FormaFarmaceutica, Producto, StockProducto, MovimientoInventario
)
from .serializers import (
    CategoriaProductoSerializer, LaboratorioSerializer, PrincipioActivoSerializer,
    FormaFarmaceuticaSerializer, ProductoSerializer, StockProductoSerializer,
    MovimientoInventarioSerializer, ProductoAutocompleteSerializer
)
from core.permissions import IsAdminOrManager, IsAdminOrSucursalManager

class CategoriaProductoViewSet(viewsets.ModelViewSet):
    queryset = CategoriaProducto.objects.all().order_by('nombre')
    serializer_class = CategoriaProductoSerializer
    permission_classes = [IsAdminOrManager]

class LaboratorioViewSet(viewsets.ModelViewSet):
    queryset = Laboratorio.objects.all().order_by('nombre')
    serializer_class = LaboratorioSerializer
    permission_classes = [IsAdminOrManager]

class PrincipioActivoViewSet(viewsets.ModelViewSet):
    queryset = PrincipioActivo.objects.all().order_by('nombre')
    serializer_class = PrincipioActivoSerializer
    permission_classes = [IsAdminOrManager]

class FormaFarmaceuticaViewSet(viewsets.ModelViewSet):
    queryset = FormaFarmaceutica.objects.all().order_by('nombre')
    serializer_class = FormaFarmaceuticaSerializer
    permission_classes = [IsAdminOrManager]

class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all().order_by('nombre')
    serializer_class = ProductoSerializer
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [IsAdminOrManager]
        return [permission() for permission in permission_classes]

class StockProductoViewSet(viewsets.ModelViewSet):
    queryset = StockProducto.objects.all().order_by('sucursal__nombre', 'producto__nombre', 'lote')
    serializer_class = StockProductoSerializer
    permission_classes = [IsAdminOrSucursalManager]

class MovimientoInventarioViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MovimientoInventario.objects.all().order_by('-fecha_movimiento')
    serializer_class = MovimientoInventarioSerializer
    permission_classes = [IsAdminOrSucursalManager]

# --- VISTA DE API PARA AUTOCOMPLETADO ---
class ProductoAutocompleteAPIView(ListAPIView):
    queryset = Producto.objects.select_related('laboratorio', 'principio_activo').all()
    serializer_class = ProductoAutocompleteSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['nombre', 'codigo_barras', 'principio_activo__nombre']