# traslados/serializers.py
from rest_framework import serializers
from .models import TransferenciaStock
from core.serializers import SucursalSerializer, UsuarioSerializer # Importamos para anidamiento
from inventario.serializers import ProductoSerializer # Importamos para anidamiento

class TransferenciaStockSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo TransferenciaStock.
    Permite serializar/deserializar los datos de una transferencia,
    incluyendo detalles de las sucursales, producto y usuarios.
    """
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    sucursal_origen_nombre = serializers.CharField(source='sucursal_origen.nombre', read_only=True)
    sucursal_destino_nombre = serializers.CharField(source='sucursal_destino.nombre', read_only=True)
    solicitado_por_username = serializers.CharField(source='solicitado_por.username', read_only=True)
    enviado_por_username = serializers.CharField(source='enviado_por.username', read_only=True)
    recibido_por_username = serializers.CharField(source='recibido_por.username', read_only=True)

    class Meta:
        model = TransferenciaStock
        fields = [
            'id', 'producto', 'producto_nombre',
            'sucursal_origen', 'sucursal_origen_nombre',
            'sucursal_destino', 'sucursal_destino_nombre',
            'cantidad', 'fecha_solicitud', 'fecha_envio', 'fecha_recepcion',
            'estado', 'solicitado_por', 'solicitado_por_username',
            'enviado_por', 'enviado_por_username',
            'recibido_por', 'recibido_por_username',
            'observaciones'
        ]
        read_only_fields = ['fecha_solicitud', 'fecha_envio', 'fecha_recepcion']

    def validate(self, data):
        """
        Valida que las sucursales de origen y destino no sean la misma
        y que pertenezcan a la misma Farmacia.
        """
        sucursal_origen = data.get('sucursal_origen')
        sucursal_destino = data.get('sucursal_destino')

        if sucursal_origen and sucursal_destino:
            if sucursal_origen == sucursal_destino:
                raise serializers.ValidationError("La sucursal de origen no puede ser la misma que la sucursal de destino.")
            if sucursal_origen.farmacia != sucursal_destino.farmacia:
                raise serializers.ValidationError("Las sucursales de origen y destino deben pertenecer a la misma Farmacia (cadena).")
        return data

    def create(self, validated_data):
        # Asigna automáticamente el usuario que solicita si no se envía.
        # Aquí, el 'solicitado_por' se establecerá en el ViewSet si no se proporciona.
        return super().create(validated_data)
