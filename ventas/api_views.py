# ventas/api_views.py
from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Venta, DetalleVenta
from .serializers import VentaSerializer, DetalleVentaSerializer
from core.permissions import IsAdminOrManager, IsAdminOrSucursalManager # Importar permisos
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction # Para transacciones atómicas

class VentaViewSet(viewsets.ModelViewSet):
    """
    API endpoint que permite a las Ventas ser vistas, creadas o editadas.
    Administradores y Gerentes de Sucursal pueden gestionar todas las ventas.
    Vendedores solo pueden crear y ver sus propias ventas.
    """
    queryset = Venta.objects.all().order_by('-fecha_venta')
    serializer_class = VentaSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'sucursal', 'cliente', 'vendedor', 'tipo_comprobante', 'metodo_pago',
        'estado_facturacion_electronica', 'fecha_venta__date__gte', 'fecha_venta__date__lte'
    ]
    search_fields = [
        'numero_comprobante', 'cliente__nombres', 'cliente__apellidos',
        'vendedor__username', 'sucursal__nombre', 'observaciones'
    ]
    ordering_fields = ['fecha_venta', 'total_venta']

    def get_permissions(self):
        # Permisos para Venta:
        if self.action in ['list', 'retrieve']:
            # Cualquiera autenticado puede ver la lista de ventas o una venta específica,
            # pero el get_queryset limitará a sus propias ventas o las de su sucursal/farmacia.
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['create']:
            # Solo Administradores, Gerentes de Sucursal y Vendedores pueden crear ventas.
            permission_classes = [IsAdminOrManager, permissions.IsAuthenticated]
        elif self.action in ['update', 'partial_update']:
            # Solo Administradores y Gerentes de Sucursal pueden actualizar ventas existentes.
            # Un vendedor no debería poder editar ventas una vez creadas (a menos que sea para su propia venta y haya lógica de negocio).
            permission_classes = [IsAdminOrManager]
        elif self.action == 'destroy':
            # Solo Administradores pueden eliminar ventas (acción de alto impacto).
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated] # Default para otras acciones
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        # Filtrar ventas según el rol del usuario
        queryset = super().get_queryset()
        user = self.request.user

        if user.is_authenticated:
            if user.is_superuser or (user.rol and user.rol.nombre == 'Administrador'):
                return queryset # Administradores y superusuarios ven todas las ventas
            elif user.rol and user.rol.nombre == 'Gerente de Sucursal' and user.sucursal:
                # Gerentes de Sucursal ven ventas de su propia sucursal y de sus vendedores asociados
                return queryset.filter(sucursal=user.sucursal) # O .filter(sucursal__farmacia=user.sucursal.farmacia) si ven todas las de su farmacia
            elif user.rol and user.rol.nombre == 'Vendedor':
                # Vendedores solo ven las ventas que ellos mismos registraron
                return queryset.filter(vendedor=user)
            else:
                return queryset.none() # Otros roles no tienen acceso a ventas
        return queryset.none() # Si no está autenticado, no ve nada

    # Al crear una venta, el vendedor se autoasigna
    def perform_create(self, serializer):
        # Asegúrate de que el vendedor se asigne automáticamente al usuario autenticado
        serializer.save(vendedor=self.request.user)

    # Acción personalizada para procesar una venta (e.g., afectar stock, emitir comprobante)
    @action(detail=True, methods=['post'], permission_classes=[IsAdminOrManager]) # Solo Administradores/Gerentes pueden procesar
    def procesar(self, request, pk=None):
        venta = self.get_object()
        if venta.estado_facturacion_electronica in ['PENDIENTE', 'N/A']:
            try:
                with transaction.atomic():
                    # Aquí iría la lógica para interactuar con los detalles de venta
                    # para decrementar el stock y registrar movimientos de inventario.
                    # Asumimos que DetalleVenta tiene un método `actualizar_stock_por_venta`.
                    for detalle in venta.detalles.all():
                        if detalle.stock_producto and detalle.stock_producto.cantidad >= detalle.cantidad:
                            detalle.actualizar_stock_por_venta(request.user) # Pasa el usuario que procesa
                        else:
                            raise ValueError(f"Stock insuficiente o lote no especificado para el producto {detalle.producto.nombre}.")

                    # Actualiza el estado de la venta
                    venta.estado_facturacion_electronica = 'ACEPTADO' # O 'ENVIADO' si hay un servicio FE real
                    venta.save()
                    venta.calcular_totales() # Recalcula totales por si acaso

                    return Response({'status': 'Venta procesada y stock actualizado.'}, status=status.HTTP_200_OK)
            except ValueError as ve:
                return Response({'error': str(ve)}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({'error': f"Error inesperado al procesar la venta: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({'status': f"La venta ya está en estado '{venta.estado_facturacion_electronica}'."}, status=status.HTTP_400_BAD_REQUEST)


class DetalleVentaViewSet(viewsets.ModelViewSet):
    """
    API endpoint para los Detalles de Venta.
    Los detalles generalmente se gestionan a través de la Venta principal,
    pero este endpoint permite operaciones CRUD directas si es necesario.
    """
    queryset = DetalleVenta.objects.all().order_by('venta', 'producto__nombre')
    serializer_class = DetalleVentaSerializer
    # Solo Administradores y Gerentes de Sucursal pueden gestionar detalles directamente.
    # La creación/edición de detalles se hará mayormente a través de la Venta.
    permission_classes = [IsAdminOrManager]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['venta', 'producto', 'unidad_venta']
    search_fields = ['producto__nombre', 'venta__numero_comprobante']
    ordering_fields = ['cantidad', 'precio_unitario']

    def get_queryset(self):
        # Filtrar detalles de venta según la sucursal de la venta padre o el rol del usuario
        queryset = super().get_queryset()
        user = self.request.user

        if user.is_authenticated and not user.is_superuser:
            if user.rol and user.rol.nombre == 'Administrador':
                return queryset # Administradores ven todos los detalles
            elif user.rol and user.rol.nombre == 'Gerente de Sucursal' and user.sucursal:
                # Gerentes de Sucursal ven detalles de ventas de su sucursal
                return queryset.filter(venta__sucursal=user.sucursal)
            elif user.rol and user.rol.nombre == 'Vendedor':
                # Vendedores ven detalles de sus propias ventas
                return queryset.filter(venta__vendedor=user)
            else:
                return queryset.none()
        return queryset.none() # No autenticado no ve nada

