# ventas/serializers.py
from rest_framework import serializers
from .models import Venta, DetalleVenta
from core.serializers import SucursalSerializer, UsuarioSerializer # Importamos para anidamiento
from clientes.serializers import ClienteSerializer # Importamos para anidamiento
from inventario.serializers import ProductoSerializer, StockProductoSerializer # Importamos para anidamiento

# Serializador para DetalleVenta
class DetalleVentaSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    stock_producto_lote = serializers.CharField(source='stock_producto.lote', read_only=True)

    class Meta:
        model = DetalleVenta
        fields = [
            'id', 'venta', 'producto', 'producto_nombre',
            'stock_producto', 'stock_producto_lote', # Para referenciar el lote específico
            'cantidad', 'unidad_venta', 'precio_unitario',
            'descuento_linea', 'subtotal_linea'
        ]
        read_only_fields = ['subtotal_linea']

# Serializador para Venta
class VentaSerializer(serializers.ModelSerializer):
    sucursal_nombre = serializers.CharField(source='sucursal.nombre', read_only=True)
    cliente_nombre_completo = serializers.CharField(source='cliente.get_full_name', read_only=True)
    vendedor_username = serializers.CharField(source='vendedor.username', read_only=True)
    # Anidar los detalles de venta. Se permite escribir los detalles al crear/actualizar una venta.
    detalles = DetalleVentaSerializer(many=True) # `read_only=False` por defecto, permite la escritura.

    class Meta:
        model = Venta
        fields = [
            'id', 'sucursal', 'sucursal_nombre',
            'cliente', 'cliente_nombre_completo',
            'vendedor', 'vendedor_username', 'fecha_venta',
            'tipo_comprobante', 'numero_comprobante', 'metodo_pago',
            'total_venta', 'subtotal', 'impuestos', 'descuento_total',
            'estado_facturacion_electronica', 'uuid_comprobante_fe',
            'detalles' # Incluir los detalles anidados para creación/actualización
        ]
        read_only_fields = [
            'fecha_venta', 'total_venta', 'subtotal', 'impuestos',
            'descuento_total', 'estado_facturacion_electronica',
            'uuid_comprobante_fe' # Estos campos se actualizan internamente
        ]

    def create(self, validated_data):
        # Extraer los detalles de la venta del validated_data
        detalles_data = validated_data.pop('detalles')
        # Crear la instancia de la Venta principal
        venta = Venta.objects.create(**validated_data)
        # Crear cada DetalleVenta y asociarlo a la Venta recién creada
        for detalle_data in detalles_data:
            DetalleVenta.objects.create(venta=venta, **detalle_data)
        venta.calcular_totales() # Recalcular los totales de la venta después de crear los detalles
        return venta

    def update(self, instance, validated_data):
        detalles_data = validated_data.pop('detalles', None) # Se ignora si no es read_only
        instance = super().update(instance, validated_data)
        instance.calcular_totales() # Recalcular los totales después de actualizar la venta
        return instance

