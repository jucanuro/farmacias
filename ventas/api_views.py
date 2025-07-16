# ventas/api_views.py

from rest_framework import viewsets, permissions, filters, serializers, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
import django_filters
from .models import Venta, DetalleVenta,SesionCaja
from .serializers import VentaSerializer, DetalleVentaSerializer,SesionCajaSerializer
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
    
    def create(self, request, *args, **kwargs):
        """
        Sobrescribe el método de creación para garantizar que se devuelva
        un solo objeto de venta y no una lista.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # El perform_create guarda el objeto en la base de datos y la instancia
        # queda guardada en 'serializer.instance'.
        self.perform_create(serializer)
        
        # ¡AQUÍ ESTÁ LA LÓGICA CLAVE!
        # En lugar de confiar en el `serializer.data` original, creamos un nuevo
        # serializador a partir de la instancia recién guardada. Esto nos da
        # la garantía de que estamos serializando un único objeto Venta.
        respuesta_serializer = self.get_serializer(serializer.instance)
        
        headers = self.get_success_headers(respuesta_serializer.data)
        
        # Devolvemos los datos del NUEVO serializador, que contiene el objeto único.
        return Response(respuesta_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

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
    
    
class SesionCajaViewSet(viewsets.ViewSet):
    """
    ViewSet para gestionar la Apertura, Cierre y Estado de la Caja.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Este ViewSet no opera sobre una lista de objetos, sino sobre el estado actual.
        return SesionCaja.objects.filter(usuario=self.request.user)

    @action(detail=False, methods=['get'])
    def estado(self, request):
        """
        Verifica el estado actual de la caja para el usuario logueado.
        URL: /api/caja/estado/
        """
        try:
            sesion_abierta = SesionCaja.objects.get(usuario=request.user, estado='ABIERTA')
            serializer = SesionCajaSerializer(sesion_abierta)
            return Response(serializer.data)
        except SesionCaja.DoesNotExist:
            return Response({'estado': 'CERRADA'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'])
    def abrir(self, request):
        """
        Abre una nueva sesión de caja con un monto inicial.
        URL: /api/caja/abrir/
        """
        sesion_existente = SesionCaja.objects.filter(usuario=request.user, estado='ABIERTA').exists()
        if sesion_existente:
            return Response({'error': 'Ya tienes una sesión de caja abierta.'}, status=status.HTTP_400_BAD_REQUEST)

        monto_inicial = request.data.get('monto_inicial')
        if monto_inicial is None:
            return Response({'error': 'El monto inicial es requerido.'}, status=status.HTTP_400_BAD_REQUEST)

        sesion = SesionCaja.objects.create(
            usuario=request.user,
            sucursal=request.user.sucursal,
            monto_inicial=monto_inicial,
            estado='ABIERTA'
        )
        serializer = SesionCajaSerializer(sesion)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def cerrar(self, request):
        """
        Cierra la sesión de caja activa del usuario.
        URL: /api/caja/cerrar/
        """
        try:
            sesion = SesionCaja.objects.get(usuario=request.user, estado='ABIERTA')
        except SesionCaja.DoesNotExist:
            return Response({'error': 'No tienes una sesión de caja abierta para cerrar.'}, status=status.HTTP_400_BAD_REQUEST)

        monto_final_real = request.data.get('monto_final_real')
        if monto_final_real is None:
            return Response({'error': 'El monto final real (conteo) es requerido.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Aquí iría la lógica para calcular el monto que debería haber según el sistema
        # Por ahora, simplemente cerramos la caja.
        sesion.monto_final_real = monto_final_real
        sesion.estado = 'CERRADA'
        sesion.fecha_cierre = timezone.now()
        # sesion.diferencia = Decimal(sesion.monto_final_real) - sesion.monto_final_sistema
        sesion.save()

        serializer = SesionCajaSerializer(sesion)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
