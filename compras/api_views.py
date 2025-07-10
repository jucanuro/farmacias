# compras/api_views.py
from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.db import transaction # Para operaciones atómicas
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from .models import (
    CotizacionProveedor, DetalleCotizacion,
    OrdenCompra, DetalleOrdenCompra,
    Compra, DetalleCompra
)
from .serializers import (
    CotizacionProveedorSerializer, DetalleCotizacionSerializer,
    OrdenCompraSerializer, DetalleOrdenCompraSerializer,
    CompraSerializer, DetalleCompraSerializer
)
from core.permissions import IsAdminOrManager, IsAdminOrSucursalManager # Importar permisos personalizados
from inventario.models import StockProducto, MovimientoInventario # Para la lógica de stock

class CotizacionProveedorViewSet(viewsets.ModelViewSet):
    """
    API endpoint para gestionar Cotizaciones de Proveedores.
    Solo administradores y gerentes de sucursal pueden ver o editar.
    Los gerentes de sucursal ven las cotizaciones creadas por ellos o para sus farmacias.
    """
    queryset = CotizacionProveedor.objects.all().order_by('-fecha_cotizacion')
    serializer_class = CotizacionProveedorSerializer
    permission_classes = [IsAdminOrManager] # Solo Administradores y Gerentes pueden gestionar cotizaciones
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['proveedor', 'estado', 'creado_por', 'fecha_cotizacion', 'fecha_validez']
    search_fields = ['numero_cotizacion', 'proveedor__nombre_comercial', 'observaciones']
    ordering_fields = ['fecha_cotizacion', 'total_cotizacion']

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_authenticated and not user.is_superuser and user.rol:
            if user.rol.nombre == 'Administrador':
                return queryset # Administradores ven todas las cotizaciones
            elif user.rol.nombre == 'Gerente de Sucursal':
                # Gerentes de Sucursal ven cotizaciones que ellos crearon o cotizaciones para su farmacia (asumiendo que hay un campo de farmacia en la cotización o se asocia con productos/sucursales)
                # Por ahora, un gerente ve las que él creó. Podríamos extender si se asocia a una Farmacia de destino.
                return queryset.filter(creado_por=user)
            else:
                return queryset.none() # Otros roles no tienen acceso
        return queryset.none() # No autenticado no ve nada

    def perform_create(self, serializer):
        serializer.save(creado_por=self.request.user)

class DetalleCotizacionViewSet(viewsets.ModelViewSet):
    """
    API endpoint para gestionar Detalles de Cotizaciones.
    Solo administradores y gerentes de sucursal pueden ver o editar.
    """
    queryset = DetalleCotizacion.objects.all().order_by('cotizacion', 'producto__nombre')
    serializer_class = DetalleCotizacionSerializer
    permission_classes = [IsAdminOrManager] # Solo Administradores y Gerentes pueden gestionar detalles
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['cotizacion', 'producto']
    search_fields = ['producto__nombre', 'cotizacion__numero_cotizacion']
    ordering_fields = ['cantidad', 'precio_unitario_cotizado']

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_authenticated and not user.is_superuser and user.rol:
            if user.rol.nombre == 'Administrador':
                return queryset
            elif user.rol.nombre == 'Gerente de Sucursal':
                # Gerentes ven detalles de cotizaciones que ellos crearon
                return queryset.filter(cotizacion__creado_por=user)
            else:
                return queryset.none()
        return queryset.none()

class OrdenCompraViewSet(viewsets.ModelViewSet):
    """
    API endpoint para gestionar Órdenes de Compra.
    Solo administradores y gerentes de sucursal pueden ver o editar.
    Los gerentes de sucursal ven las OC para su sucursal de destino.
    """
    queryset = OrdenCompra.objects.all().order_by('-fecha_orden')
    serializer_class = OrdenCompraSerializer
    permission_classes = [IsAdminOrManager] # Solo Administradores y Gerentes pueden gestionar OC
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['proveedor', 'sucursal_destino', 'estado', 'creado_por', 'fecha_orden']
    search_fields = ['numero_orden', 'proveedor__nombre_comercial', 'observaciones']
    ordering_fields = ['fecha_orden', 'total_orden']

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_authenticated and not user.is_superuser and user.rol:
            if user.rol.nombre == 'Administrador':
                return queryset
            elif user.rol.nombre == 'Gerente de Sucursal' and user.sucursal:
                # Gerentes de Sucursal ven OC destinadas a su sucursal
                return queryset.filter(sucursal_destino=user.sucursal)
            else:
                return queryset.none()
        return queryset.none()

    def perform_create(self, serializer):
        serializer.save(creado_por=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminOrManager])
    def marcar_enviada(self, request, pk=None):
        orden_compra = self.get_object()
        if orden_compra.estado == 'PENDIENTE':
            orden_compra.estado = 'ENVIADA'
            orden_compra.save()
            return Response({'status': 'Orden de Compra marcada como enviada.'}, status=status.HTTP_200_OK)
        return Response({'error': 'La Orden de Compra no puede ser marcada como enviada en su estado actual.'}, status=status.HTTP_400_BAD_REQUEST)

class DetalleOrdenCompraViewSet(viewsets.ModelViewSet):
    """
    API endpoint para gestionar Detalles de Órdenes de Compra.
    Solo administradores y gerentes de sucursal pueden ver o editar.
    """
    queryset = DetalleOrdenCompra.objects.all().order_by('orden_compra', 'producto__nombre')
    serializer_class = DetalleOrdenCompraSerializer
    permission_classes = [IsAdminOrManager] # Solo Administradores y Gerentes pueden gestionar detalles
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['orden_compra', 'producto']
    search_fields = ['producto__nombre', 'orden_compra__numero_orden']
    ordering_fields = ['cantidad_solicitada', 'precio_unitario_oc']

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_authenticated and not user.is_superuser and user.rol:
            if user.rol.nombre == 'Administrador':
                return queryset
            elif user.rol.nombre == 'Gerente de Sucursal' and user.sucursal:
                # Gerentes ven detalles de OC destinadas a su sucursal
                return queryset.filter(orden_compra__sucursal_destino=user.sucursal)
            else:
                return queryset.none()
        return queryset.none()

class CompraViewSet(viewsets.ModelViewSet):
    """
    API endpoint para gestionar Compras (recepciones de productos).
    Administradores y Gerentes de Sucursal pueden gestionar.
    Los gerentes de sucursal ven las compras para su sucursal.
    """
    queryset = Compra.objects.all().order_by('-fecha_recepcion')
    serializer_class = CompraSerializer
    permission_classes = [IsAdminOrManager] # Solo Administradores y Gerentes pueden gestionar compras
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['proveedor', 'sucursal_destino', 'estado', 'registrado_por', 'fecha_recepcion']
    search_fields = ['numero_factura_proveedor', 'proveedor__nombre_comercial', 'observaciones']
    ordering_fields = ['fecha_recepcion', 'total_compra']

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Compra.objects.none()
        if user.is_superuser:
            return Compra.objects.all().order_by('-fecha_recepcion')

        if hasattr(user, 'rol') and user.rol:
            if user.rol.nombre == 'Administrador':
                return Compra.objects.all().order_by('-fecha_recepcion')
            
            if user.rol.nombre == 'Gerente de Sucursal' and hasattr(user, 'sucursal') and user.sucursal:
                return Compra.objects.filter(sucursal_destino=user.sucursal).order_by('-fecha_recepcion')

        return Compra.objects.none()

    def perform_create(self, serializer):
        serializer.save(registrado_por=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminOrManager])
    def procesar(self, request, pk=None):
        compra = self.get_object()
        if compra.estado == 'PENDIENTE':
            try:
                with transaction.atomic():
                    for detalle in compra.detalles.all():
                        detalle.actualizar_stock_por_compra(request.user) # Actualiza stock y registra movimiento
                    compra.estado = 'PROCESADA'
                    compra.save()
                    return Response({'status': 'Compra procesada y stock actualizado.'}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'error': f"Error al procesar la compra: {e}"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': 'La compra no puede ser procesada en su estado actual.'}, status=status.HTTP_400_BAD_REQUEST)

class DetalleCompraViewSet(viewsets.ModelViewSet):
    """
    API endpoint para gestionar Detalles de Compras.
    Solo administradores y gerentes de sucursal pueden ver o editar.
    """
    queryset = DetalleCompra.objects.all().order_by('compra', 'producto__nombre', 'lote')
    serializer_class = DetalleCompraSerializer
    permission_classes = [IsAdminOrManager] # Solo Administradores y Gerentes pueden gestionar detalles
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['compra', 'producto', 'lote', 'fecha_vencimiento']
    search_fields = ['producto__nombre', 'lote', 'compra__numero_factura_proveedor']
    ordering_fields = ['cantidad_recibida', 'fecha_vencimiento']

    def get_queryset(self):
        user = self.request.user

        # Si el usuario no está autenticado, no devuelve nada.
        if not user.is_authenticated:
            return DetalleCompra.objects.none()

        # Si es superusuario, debe ver TODO, sin filtros.
        if user.is_superuser:
            return DetalleCompra.objects.all().order_by('compra', 'producto__nombre', 'lote')

        # Si es un usuario normal, aplicamos la lógica de roles.
        if hasattr(user, 'rol') and user.rol:
            if user.rol.nombre == 'Administrador':
                return DetalleCompra.objects.all().order_by('compra', 'producto__nombre', 'lote')
            
            if user.rol.nombre == 'Gerente de Sucursal' and hasattr(user, 'sucursal') and user.sucursal:
                # Gerentes solo ven detalles de compras para SU sucursal.
                return DetalleCompra.objects.filter(compra__sucursal_destino=user.sucursal).order_by('compra', 'producto__nombre', 'lote')

        # Si no cumple ninguna condición, no ve nada.
        return DetalleCompra.objects.none()

