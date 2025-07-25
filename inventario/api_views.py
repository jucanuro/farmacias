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

class ProductoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet de SOLO LECTURA para listar y buscar productos.
    El POS solo necesita leer, no crear o modificar el catálogo maestro.
    """
    queryset = Producto.objects.all().order_by('nombre')
    serializer_class = ProductoSerializer
    permission_classes = [permissions.IsAuthenticated] # Permiso simple para leer
    
    # Aquí puedes añadir tus filtros si los necesitas
    # filter_backends = [...]
    # search_fields = [...]

    def get_serializer_context(self):
        """
        Esta función crucial pasa el objeto 'request' al serializador.
        Así, el serializador puede acceder a request.user.sucursal.
        """
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

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


class StockAutocompleteAPIView(ListAPIView):
    """
    API para buscar lotes de StockProducto con existencias (> 0)
    en una sucursal específica.
    """
    serializer_class = StockProductoSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = StockProducto.objects.select_related('producto').filter(cantidad__gt=0)
        
        sucursal_id = self.request.query_params.get('sucursal_id')
        if not sucursal_id:
            return StockProducto.objects.none()
        queryset = queryset.filter(sucursal_id=sucursal_id)

        search_term = self.request.query_params.get('search')
        if search_term:
            queryset = queryset.filter(producto__nombre__icontains=search_term)
            
        return queryset.order_by('producto__nombre', 'fecha_vencimiento')