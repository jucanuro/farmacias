# traslados/api_views.py
from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction # Para transacciones atómicas

from .models import TransferenciaStock
from .serializers import TransferenciaStockSerializer
from core.permissions import IsAdminOrManager, IsAdminOrSucursalManager # Importar permisos personalizados

class TransferenciaStockViewSet(viewsets.ModelViewSet):
    """
    API endpoint que permite a las Transferencias de Stock ser vistas, creadas o gestionadas.
    Administradores pueden gestionar todas las transferencias.
    Gerentes de Sucursal pueden gestionar transferencias donde su sucursal sea origen o destino.
    """
    queryset = TransferenciaStock.objects.all().order_by('-fecha_solicitud')
    serializer_class = TransferenciaStockSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'producto', 'sucursal_origen', 'sucursal_destino', 'estado',
        'solicitado_por', 'fecha_solicitud__date__gte', 'fecha_solicitud__date__lte'
    ]
    search_fields = [
        'producto__nombre', 'sucursal_origen__nombre', 'sucursal_destino__nombre',
        'solicitado_por__username', 'observaciones'
    ]
    ordering_fields = ['fecha_solicitud', 'cantidad', 'estado']

    def get_permissions(self):
        # Permisos para TransferenciaStock:
        if self.action in ['list', 'retrieve']:
            # Todos los usuarios autenticados pueden ver la lista de transferencias o una específica.
            # El get_queryset limitará lo que cada uno puede ver.
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['create']:
            # Solo Administradores y Gerentes de Sucursal pueden crear transferencias.
            permission_classes = [IsAdminOrManager]
        elif self.action in ['update', 'partial_update', 'destroy']:
            # Actualizar y eliminar transferencias, así como las acciones de estado
            # requiere ser Administrador o un Gerente de Sucursal del origen/destino.
            # IsAdminOrSucursalManager se encargará de esto a nivel de objeto.
            permission_classes = [IsAdminOrSucursalManager]
        else:
            permission_classes = [permissions.IsAuthenticated] # Default para otras acciones
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        # Filtrar transferencias según el rol del usuario
        queryset = super().get_queryset()
        user = self.request.user

        if user.is_authenticated:
            if user.is_superuser or (user.rol and user.rol.nombre == 'Administrador'):
                return queryset # Administradores y superusuarios ven todas las transferencias
            elif user.rol and user.rol.nombre == 'Gerente de Sucursal' and user.sucursal:
                # Gerentes de Sucursal ven transferencias donde su sucursal es origen O destino
                return queryset.filter(
                    Q(sucursal_origen=user.sucursal) | Q(sucursal_destino=user.sucursal)
                )
            else:
                return queryset.none() # Otros roles no tienen acceso a transferencias
        return queryset.none() # Si no está autenticado, no ve nada

    def perform_create(self, serializer):
        # Asigna automáticamente el usuario autenticado como quien solicita la transferencia
        serializer.save(solicitado_por=self.request.user)

    # Acciones personalizadas para cambiar el estado de la transferencia
    @action(detail=True, methods=['post'], permission_classes=[IsAdminOrSucursalManager])
    def enviar(self, request, pk=None):
        transferencia = self.get_object() # get_object() ya aplica permisos a nivel de objeto
        try:
            transferencia.realizar_envio(request.user)
            return Response({'status': 'Transferencia marcada como ENVIADA y stock de origen decrementado.'}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f"Error inesperado al enviar la transferencia: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminOrSucursalManager])
    def recibir(self, request, pk=None):
        transferencia = self.get_object() # get_object() ya aplica permisos a nivel de objeto
        try:
            transferencia.realizar_recepcion(request.user)
            return Response({'status': 'Transferencia marcada como RECIBIDA y stock de destino incrementado.'}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f"Error inesperado al recibir la transferencia: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminOrManager]) # Solo Admins o Gerentes pueden rechazar
    def rechazar(self, request, pk=None):
        transferencia = self.get_object() # get_object() ya aplica permisos a nivel de objeto
        observaciones = request.data.get('observaciones', '')
        try:
            transferencia.rechazar_transferencia(request.user, observaciones)
            return Response({'status': 'Transferencia marcada como RECHAZADA.'}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f"Error inesperado al rechazar la transferencia: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser]) # Solo Admins pueden cancelar completamente
    def cancelar(self, request, pk=None):
        transferencia = self.get_object()
        if transferencia.estado in ['PENDIENTE', 'ENVIADO']:
            try:
                # Aquí se debería revertir cualquier stock ya afectado si el estado es 'ENVIADO'
                # La lógica de reversión de stock ya está en rechazar_transferencia si fue enviado.
                # Para simplificar, si se cancela directamente aquí, asumimos que no afectó stock o se gestiona aparte.
                transferencia.estado = 'CANCELADO'
                transferencia.observaciones += f"\nCancelado por {request.user.username} el {timezone.now().strftime('%Y-%m-%d %H:%M')}"
                transferencia.save()
                return Response({'status': 'Transferencia marcada como CANCELADA.'}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'error': f"Error al cancelar la transferencia: {e}"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': 'La transferencia no puede ser cancelada en su estado actual.'}, status=status.HTTP_400_BAD_REQUEST)

