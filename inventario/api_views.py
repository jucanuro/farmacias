# inventario/api_views.py
from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q # Para filtros complejos en get_queryset

from .models import (
    CategoriaProducto, Laboratorio, PrincipioActivo,
    FormaFarmaceutica, Producto, StockProducto, MovimientoInventario
)
from .serializers import (
    CategoriaProductoSerializer, LaboratorioSerializer, PrincipioActivoSerializer,
    FormaFarmaceuticaSerializer, ProductoSerializer, StockProductoSerializer,
    MovimientoInventarioSerializer
)
from core.permissions import IsAdminOrManager, IsAdminOrSucursalManager # Importar permisos personalizados

class CategoriaProductoViewSet(viewsets.ModelViewSet):
    """
    API endpoint que permite a las Categorías de Producto ser vistas o editadas.
    Solo administradores y gerentes de sucursal pueden gestionar categorías.
    """
    queryset = CategoriaProducto.objects.all().order_by('nombre')
    serializer_class = CategoriaProductoSerializer
    permission_classes = [IsAdminOrManager] # Solo Administradores y Gerentes pueden gestionar categorías
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['nombre']
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['nombre']

class LaboratorioViewSet(viewsets.ModelViewSet):
    """
    API endpoint que permite a los Laboratorios ser vistos o editados.
    Solo administradores y gerentes de sucursal pueden gestionar laboratorios.
    """
    queryset = Laboratorio.objects.all().order_by('nombre')
    serializer_class = LaboratorioSerializer
    permission_classes = [IsAdminOrManager] # Solo Administradores y Gerentes pueden gestionar laboratorios
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['nombre']
    search_fields = ['nombre', 'direccion', 'telefono']
    ordering_fields = ['nombre']

class PrincipioActivoViewSet(viewsets.ModelViewSet):
    """
    API endpoint que permite a los Principios Activos ser vistos o editados.
    Solo administradores y gerentes de sucursal pueden gestionar principios activos.
    """
    queryset = PrincipioActivo.objects.all().order_by('nombre')
    serializer_class = PrincipioActivoSerializer
    permission_classes = [IsAdminOrManager] # Solo Administradores y Gerentes pueden gestionar principios activos
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['nombre']
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['nombre']

class FormaFarmaceuticaViewSet(viewsets.ModelViewSet):
    """
    API endpoint que permite a las Formas Farmacéuticas ser vistas o editadas.
    Solo administradores y gerentes de sucursal pueden gestionar formas farmacéuticas.
    """
    queryset = FormaFarmaceutica.objects.all().order_by('nombre')
    serializer_class = FormaFarmaceuticaSerializer
    permission_classes = [IsAdminOrManager] # Solo Administradores y Gerentes pueden gestionar formas farmacéuticas
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['nombre']
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['nombre']

class ProductoViewSet(viewsets.ModelViewSet):
    """
    API endpoint que permite a los Productos ser vistos o editados.
    Todos los usuarios autenticados pueden ver productos.
    Solo administradores y gerentes de sucursal pueden crear/editar/eliminar productos.
    """
    queryset = Producto.objects.all().order_by('nombre')
    serializer_class = ProductoSerializer
    # Permiso para crear/editar/eliminar: IsAdminOrManager
    # Permiso para ver (GET): IsAuthenticated (todos los usuarios autenticados pueden ver productos)
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated] # Cualquiera autenticado puede ver productos
        else:
            permission_classes = [IsAdminOrManager] # Solo admins/gerentes pueden crear/actualizar/eliminar
        return [permission() for permission in permission_classes]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'categoria', 'laboratorio', 'aplica_receta', 'es_controlado',
        'forma_farmaceutica', 'presentacion_base', 'principio_activo'
    ]
    search_fields = [
        'nombre', 'codigo_barras', 'descripcion', 'principio_activo__nombre',
        'laboratorio__nombre', 'categoria__nombre'
    ]
    ordering_fields = [
        'nombre', 'precio_compra_promedio', 'margen_ganancia_sugerido'
    ]

class StockProductoViewSet(viewsets.ModelViewSet):
    """
    API endpoint que permite al Stock de Producto ser visto o editado.
    Administradores ven todo el stock. Gerentes de Sucursal ven el stock de su sucursal.
    """
    queryset = StockProducto.objects.all().order_by('sucursal__nombre', 'producto__nombre', 'lote')
    serializer_class = StockProductoSerializer
    # Permiso: IsAdminOrSucursalManager aplicará la lógica de objeto para restringir el acceso por sucursal.
    permission_classes = [IsAdminOrSucursalManager]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'sucursal', 'producto', 'lote', 'fecha_vencimiento__date__gte',
        'fecha_vencimiento__date__lte', 'producto__categoria', 'producto__laboratorio'
    ]
    search_fields = [
        'producto__nombre', 'lote', 'sucursal__nombre', 'ubicacion_almacen'
    ]
    ordering_fields = [
        'cantidad', 'fecha_vencimiento', 'sucursal__nombre', 'producto__nombre'
    ]

    def get_queryset(self):
        # Filtrar stock por la sucursal del usuario o la farmacia a la que pertenece.
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_authenticated and not user.is_superuser:
            if user.rol and user.rol.nombre == 'Administrador':
                return queryset # Administradores ven todo el stock
            elif user.rol and user.rol.nombre == 'Gerente de Sucursal' and user.sucursal:
                return queryset.filter(sucursal=user.sucursal) # Gerentes de Sucursal ven solo su stock
            elif user.farmacia: # Otros usuarios de una farmacia ven el stock de todas las sucursales de su farmacia
                return queryset.filter(sucursal__farmacia=user.farmacia)
            else:
                return queryset.none() # Si no tiene rol o asociación, no ve nada.
        return queryset # Superusuarios ven todo

class MovimientoInventarioViewSet(viewsets.ReadOnlyModelViewSet): # Solo lectura para trazabilidad
    """
    API endpoint que permite a los Movimientos de Inventario ser vistos.
    Solo lectura para asegurar la trazabilidad.
    Administradores ven todos los movimientos. Gerentes de Sucursal ven los de su sucursal.
    """
    queryset = MovimientoInventario.objects.all().order_by('-fecha_movimiento')
    serializer_class = MovimientoInventarioSerializer
    # Permiso: IsAdminOrSucursalManager aplicará la lógica de objeto para restringir el acceso por sucursal.
    permission_classes = [IsAdminOrSucursalManager]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'tipo_movimiento', 'sucursal', 'producto', 'usuario',
        'fecha_movimiento__date__gte', 'fecha_movimiento__date__lte',
        'producto__categoria', 'producto__laboratorio'
    ]
    search_fields = [
        'producto__nombre', 'sucursal__nombre', 'usuario__username',
        'referencia_doc', 'observaciones', 'stock_afectado__lote'
    ]
    ordering_fields = ['fecha_movimiento', 'cantidad', 'tipo_movimiento']

    def get_queryset(self):
        # Filtrar movimientos por la sucursal del usuario o la farmacia a la que pertenece.
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_authenticated and not user.is_superuser:
            if user.rol and user.rol.nombre == 'Administrador':
                return queryset # Administradores ven todos los movimientos
            elif user.rol and user.rol.nombre == 'Gerente de Sucursal' and user.sucursal:
                return queryset.filter(sucursal=user.sucursal) # Gerentes de Sucursal ven solo los de su sucursal
            elif user.farmacia: # Otros usuarios de una farmacia ven los movimientos de todas las sucursales de su farmacia
                return queryset.filter(sucursal__farmacia=user.farmacia)
            else:
                return queryset.none() # Si no tiene rol o asociación, no ve nada.
        return queryset # Superusuarios ven todos
