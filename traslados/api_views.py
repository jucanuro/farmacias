# traslados/api_views.py
from rest_framework import viewsets, permissions, status
from rest_framework.generics import ListAPIView
from django.core.exceptions import ValidationError
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import Transferencia
from .serializers import TransferenciaSerializer

from inventario.models import StockProducto
from inventario.serializers import StockProductoSerializer

class TransferenciaViewSet(viewsets.ModelViewSet):
    queryset = Transferencia.objects.prefetch_related('detalles__producto').all()
    serializer_class = TransferenciaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return super().get_queryset()
        # Filtra para que el usuario solo vea traslados de su farmacia
        farmacia = user.sucursal.farmacia
        return super().get_queryset().filter(
            Q(sucursal_origen__farmacia=farmacia) | Q(sucursal_destino__farmacia=farmacia)
        )

    @action(detail=True, methods=['post'])
    def enviar(self, request, pk=None):
        transferencia = self.get_object()
        try:
            transferencia.marcar_como_enviada(request.user)
            return Response({'status': 'Transferencia enviada y stock de origen actualizado.'})
        except ValidationError as e:
            return Response({'error': e.message}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def recibir(self, request, pk=None):
        transferencia = self.get_object()
        try:
            transferencia.marcar_como_recibida(request.user)
            return Response({'status': 'Transferencia recibida y stock de destino actualizado.'})
        except ValidationError as e:
            return Response({'error': e.message}, status=status.HTTP_400_BAD_REQUEST)
        
    
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
            
        return queryset.order_by('fecha_vencimiento', 'id')