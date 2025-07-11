# ventas/api_views.py

from rest_framework import viewsets, permissions, filters, serializers, status
from django_filters.rest_framework import DjangoFilterBackend
import django_filters
from .models import Venta, DetalleVenta
from .serializers import VentaSerializer, DetalleVentaSerializer
from core.permissions import IsAdminOrManager
from rest_framework.decorators import action
from django.db import transaction

# --- CLASE DE FILTRO PERSONALIZADA ---
class VentaFilter(django_filters.FilterSet):
    fecha_venta__date__gte = django_filters.DateFilter(field_name='fecha_venta__date', lookup_expr='gte')
    fecha_venta__date__lte = django_filters.DateFilter(field_name='fecha_venta__date', lookup_expr='lte')

    class Meta:
        model = Venta
        fields = [
            'sucursal', 'cliente', 'vendedor', 'tipo_comprobante', 
            'metodo_pago', 'estado', 'estado_facturacion_electronica',
            'fecha_venta__date__gte', 'fecha_venta__date__lte'
        ]

class VentaViewSet(viewsets.ModelViewSet):
    queryset = Venta.objects.all().order_by('-fecha_venta')
    serializer_class = VentaSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    # --- CONFIGURACIÓN DE FILTROS CORREGIDA ---
    filterset_class = VentaFilter
    
    search_fields = [
        'numero_comprobante', 'cliente__nombres', 'cliente__apellidos',
        'vendedor__username', 'sucursal__nombre', 'observaciones_fe'
    ]
    ordering_fields = ['fecha_venta', 'total_venta']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['create']:
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [IsAdminOrManager]
        elif self.action == 'destroy':
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_authenticated:
            if user.is_superuser or (hasattr(user, 'rol') and user.rol and user.rol.nombre == 'Administrador'):
                return queryset
            elif hasattr(user, 'rol') and user.rol and user.rol.nombre == 'Gerente de Sucursal' and user.sucursal:
                return queryset.filter(sucursal=user.sucursal)
            elif hasattr(user, 'rol') and user.rol and user.rol.nombre == 'Vendedor':
                return queryset.filter(vendedor=user)
            else:
                return queryset.none()
        return queryset.none()

    def perform_create(self, serializer):
        if not self.request.user.sucursal:
            raise serializers.ValidationError({"detail": "El usuario vendedor no tiene una sucursal asignada."})
        serializer.save(
            vendedor=self.request.user,
            sucursal=self.request.user.sucursal
        )

    @action(detail=True, methods=['post'], permission_classes=[IsAdminOrManager])
    def procesar(self, request, pk=None):
        venta = self.get_object()
        if venta.estado == 'PENDIENTE':
            try:
                with transaction.atomic():
                    for detalle in venta.detalles.all():
                        if not hasattr(detalle, 'actualizar_stock_por_venta'):
                            raise ValueError(f"El modelo DetalleVenta no tiene el método 'actualizar_stock_por_venta'.")
                        detalle.actualizar_stock_por_venta(request.user)
                    venta.estado = 'COMPLETADA'
                    if venta.tipo_comprobante in ['BOLETA', 'FACTURA']:
                        venta.estado_facturacion_electronica = 'PENDIENTE'
                    else:
                        venta.estado_facturacion_electronica = 'N/A'
                    venta.save()
                    return Response({'status': 'Venta procesada y stock actualizado.'}, status=status.HTTP_200_OK)
            except ValueError as ve:
                return Response({'error': str(ve)}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({'error': f"Error inesperado al procesar la venta: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({'status': f"La venta ya está en estado '{venta.estado}' y no puede ser procesada de nuevo."}, status=status.HTTP_400_BAD_REQUEST)

class DetalleVentaViewSet(viewsets.ModelViewSet):
    queryset = DetalleVenta.objects.all().order_by('venta', 'producto__nombre')
    serializer_class = DetalleVentaSerializer
    permission_classes = [IsAdminOrManager]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['venta', 'producto']
    search_fields = ['producto__nombre', 'venta__numero_comprobante']
    ordering_fields = ['cantidad', 'precio_unitario']

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_authenticated:
            if user.is_superuser or (hasattr(user, 'rol') and user.rol and user.rol.nombre == 'Administrador'):
                return queryset
            elif hasattr(user, 'rol') and user.rol and user.rol.nombre == 'Gerente de Sucursal' and user.sucursal:
                return queryset.filter(venta__sucursal=user.sucursal)
            elif hasattr(user, 'rol') and user.rol and user.rol.nombre == 'Vendedor':
                return queryset.filter(venta__vendedor=user)
            else:
                return queryset.none()
        return queryset.none()