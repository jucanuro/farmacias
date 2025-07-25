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
from decimal import Decimal
from django.db.models import Sum
from django.utils import timezone


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
    filterset_class = VentaFilter
    search_fields = [
        'numero_comprobante', 'cliente__nombres', 'cliente__apellidos',
        'vendedor__username', 'sucursal__nombre', 'observaciones_fe'
    ]
    ordering_fields = ['fecha_venta', 'total_venta']

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'create']:
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
        if not hasattr(self.request.user, 'sucursal') or not self.request.user.sucursal:
            raise serializers.ValidationError({"detail": "El usuario vendedor no tiene una sucursal asignada."})
        serializer.save(
            vendedor=self.request.user,
            sucursal=self.request.user.sucursal
        )
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        respuesta_serializer = self.get_serializer(serializer.instance)
        headers = self.get_success_headers(respuesta_serializer.data)
        return Response(respuesta_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['post'])
    def procesar(self, request, pk=None):
        venta = self.get_object()
        
        if venta.estado == 'COMPLETADA':
            try:
                with transaction.atomic():
                    for detalle in venta.detalles.all():
                        detalle.actualizar_stock_por_venta()
                    
                    venta.estado = 'PROCESADA'
                    
                    if venta.tipo_comprobante in ['BOLETA', 'FACTURA']:
                        venta.estado_facturacion_electronica = 'PENDIENTE'
                    else:
                        venta.estado_facturacion_electronica = 'N/A'
                    
                    venta.save()
                    return Response({'status': 'Venta procesada y stock actualizado.'}, status=status.HTTP_200_OK)

            except ValidationError as ve:
                return Response({'error': str(ve.message)}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({'error': f"Error inesperado: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(
            {'status': f"La venta ya está en estado '{venta.estado}' y no se puede procesar."},
            status=status.HTTP_400_BAD_REQUEST
        )

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

        if not request.user.sucursal:
            return Response(
                {'error': 'Tu usuario no tiene una sucursal asignada. Contacta a un administrador.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        monto_inicial = request.data.get('monto_inicial')

        # --- LÍNEA DE DEPURACIÓN ---
        # Esto imprimirá en tu terminal (donde ejecutas runserver) el valor exacto recibido.
        print(f"Valor recibido para monto_inicial: '{monto_inicial}' (Tipo: {type(monto_inicial)})")

        # --- VALIDACIÓN MEJORADA ---
        # Verifica si el valor es nulo o una cadena vacía.
        if monto_inicial is None or str(monto_inicial).strip() == '':
            return Response({'error': 'El monto inicial es requerido.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            monto_inicial_decimal = Decimal(monto_inicial)
        except Exception as e:
                # Devolvemos un error más específico para entender la causa
                return Response({'error': f"El monto '{monto_inicial}' no se pudo convertir a número. Error: {e}"}, status=status.HTTP_400_BAD_REQUEST)

        sesion = SesionCaja.objects.create(
            usuario=request.user,
            sucursal=request.user.sucursal, # Ahora sabemos que este valor existe.
            monto_inicial=monto_inicial_decimal,
            estado='ABIERTA'
        )
        serializer = SesionCajaSerializer(sesion)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def cerrar(self, request):
        """
        Cierra la sesión de caja activa del usuario, calculando los totales
        y la diferencia.
        URL: /api/caja/cerrar/
        """
        try:
            sesion = SesionCaja.objects.get(usuario=request.user, estado='ABIERTA')
        except SesionCaja.DoesNotExist:
            return Response({'error': 'No tienes una sesión de caja abierta para cerrar.'}, status=status.HTTP_400_BAD_REQUEST)

        monto_final_real_str = request.data.get('monto_final_real')
        if monto_final_real_str is None:
            return Response({'error': 'El monto final real (conteo) es requerido.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            monto_final_real = Decimal(monto_final_real_str)
        except:
            return Response({'error': 'El monto final real debe ser un número válido.'}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Calcular el total de ventas en efectivo de ESTA sesión
        total_ventas_efectivo = Venta.objects.filter(
            sesion_caja=sesion,
            metodo_pago='EFECTIVO',
            estado='COMPLETADA'
        ).aggregate(
            total=Sum('total_venta')
        )['total'] or Decimal('0.0')

        # 2. Calcular el monto que debería haber en caja según el sistema
        monto_final_sistema = sesion.monto_inicial + total_ventas_efectivo
        
        # 3. Calcular la diferencia
        diferencia = monto_final_real - monto_final_sistema
        
        # 4. Actualizar la sesión con todos los datos calculados
        sesion.monto_final_sistema = monto_final_sistema
        sesion.monto_final_real = monto_final_real
        sesion.diferencia = diferencia
        sesion.estado = 'CERRADA'
        sesion.fecha_cierre = timezone.now()
        sesion.observaciones = request.data.get('observaciones', '') # Opcional
        sesion.save()

        serializer = SesionCajaSerializer(sesion)
        return Response(serializer.data, status=status.HTTP_200_OK)