# traslados/serializers.py

from rest_framework import serializers
from django.db import transaction
from .models import Transferencia, DetalleTransferencia
from inventario.models import StockProducto # Importamos StockProducto

class DetalleTransferenciaSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    lote = serializers.CharField(source='stock_origen.lote', read_only=True)

    class Meta:
        model = DetalleTransferencia
        fields = ['id', 'producto', 'producto_nombre', 'stock_origen', 'lote', 'cantidad']


# --- 1. CREAMOS UN SERIALIZADOR AUXILIAR SOLO PARA LA ESCRITURA ---
class DetalleTransferenciaWriteSerializer(serializers.Serializer):
    stock_origen_id = serializers.IntegerField()
    cantidad = serializers.IntegerField(min_value=1)


class TransferenciaSerializer(serializers.ModelSerializer):
    detalles = DetalleTransferenciaSerializer(many=True, read_only=True)
    
    # --- 2. USAMOS EL NUEVO SERIALIZADOR AQUÍ ---
    # En lugar de ListField y DictField, usamos el serializer que acabamos de crear.
    detalles_write = DetalleTransferenciaWriteSerializer(many=True, write_only=True)
    
    sucursal_origen_nombre = serializers.CharField(source='sucursal_origen.nombre', read_only=True)
    sucursal_destino_nombre = serializers.CharField(source='sucursal_destino.nombre', read_only=True)
    solicitado_por_username = serializers.CharField(source='solicitado_por.username', read_only=True)

    class Meta:
        model = Transferencia
        fields = [
            'id', 'sucursal_origen', 'sucursal_destino', 'estado', 
            'solicitado_por', 'fecha_creacion', 'observaciones',
            'detalles', 'detalles_write',
            'sucursal_origen_nombre', 'sucursal_destino_nombre', 'solicitado_por_username'
        ]
        read_only_fields = ['estado', 'solicitado_por', 'fecha_creacion']

    def validate(self, data):
        if data['sucursal_origen'] == data['sucursal_destino']:
            raise serializers.ValidationError("Las sucursales de origen y destino no pueden ser la misma.")
        return data

    def create(self, validated_data):
        detalles_data = validated_data.pop('detalles_write')
        usuario = self.context['request'].user

        with transaction.atomic():
            transferencia = Transferencia.objects.create(solicitado_por=usuario, **validated_data)
            for detalle_data in detalles_data:
                # Obtenemos el objeto StockProducto para validar y obtener el producto
                try:
                    stock_origen = StockProducto.objects.get(id=detalle_data['stock_origen_id'])
                except StockProducto.DoesNotExist:
                    raise serializers.ValidationError(f"El lote de stock con ID {detalle_data['stock_origen_id']} no existe.")

                DetalleTransferencia.objects.create(
                    transferencia=transferencia,
                    stock_origen=stock_origen,
                    cantidad=detalle_data['cantidad'],
                    producto=stock_origen.producto
                )
        return transferencia