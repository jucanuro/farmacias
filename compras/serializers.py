# compras/serializers.py
from rest_framework import serializers
from .models import (
    CotizacionProveedor, DetalleCotizacion,
    OrdenCompra, DetalleOrdenCompra,
    Compra, DetalleCompra
)
from proveedores.serializers import ProveedorSerializer # Importamos para anidamiento
from inventario.serializers import ProductoSerializer, StockProductoSerializer, MovimientoInventarioSerializer # Importamos para anidamiento
from core.serializers import SucursalSerializer, UsuarioSerializer # Importamos para anidamiento

# Serializador para DetalleCotizacion
class DetalleCotizacionSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)

    class Meta:
        model = DetalleCotizacion
        fields = [
            'id', 'cotizacion', 'producto', 'producto_nombre',
            'cantidad', 'precio_unitario_cotizado', 'subtotal_linea'
        ]
        read_only_fields = ['subtotal_linea']

# Serializador para CotizacionProveedor
class CotizacionProveedorSerializer(serializers.ModelSerializer):
    proveedor_nombre = serializers.CharField(source='proveedor.nombre_comercial', read_only=True)
    creado_por_username = serializers.CharField(source='creado_por.username', read_only=True)
    detalles = DetalleCotizacionSerializer(many=True, read_only=True) # Anidamos los detalles

    class Meta:
        model = CotizacionProveedor
        fields = [
            'id', 'proveedor', 'proveedor_nombre', 'fecha_cotizacion', 'fecha_validez',
            'numero_cotizacion', 'subtotal', 'impuestos', 'total_cotizacion',
            'estado', 'observaciones', 'creado_por', 'creado_por_username',
            'fecha_creacion', 'detalles' # Incluir los detalles anidados
        ]
        read_only_fields = ['subtotal', 'impuestos', 'total_cotizacion', 'fecha_creacion']

    def create(self, validated_data):
        # Manejar la creación de detalles si se envían anidados para la creación
        detalles_data = validated_data.pop('detalles', [])
        cotizacion = CotizacionProveedor.objects.create(**validated_data)
        for detalle_data in detalles_data:
            DetalleCotizacion.objects.create(cotizacion=cotizacion, **detalle_data)
        cotizacion.calcular_totales() # Recalcular totales después de crear detalles
        return cotizacion

    def update(self, instance, validated_data):
        # Manejar la actualización de detalles si se envían anidados
        detalles_data = validated_data.pop('detalles', [])
        instance = super().update(instance, validated_data)

        # Si quieres actualizar o crear nuevos detalles anidados, aquí iría la lógica
        # Para ModelSerializer simple, esto es más complejo y usualmente se hace
        # con un ViewSet separado para DetalleCotizacion o usando `create`/`update` explícitos
        # con lógica de eliminación/actualización de sub-objetos.
        # Por ahora, los detalles anidados son read_only en update para simplificar.

        instance.calcular_totales() # Recalcular totales después de actualizar
        return instance


# Serializador para DetalleOrdenCompra
class DetalleOrdenCompraSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)

    class Meta:
        model = DetalleOrdenCompra
        fields = [
            'id', 'orden_compra', 'producto', 'producto_nombre',
            'cantidad_solicitada', 'cantidad_recibida', 'precio_unitario_oc', 'subtotal_linea'
        ]
        read_only_fields = ['subtotal_linea', 'cantidad_recibida'] # cantidad_recibida se actualiza en Compra


# Serializador para OrdenCompra
class OrdenCompraSerializer(serializers.ModelSerializer):
    proveedor_nombre = serializers.CharField(source='proveedor.nombre_comercial', read_only=True)
    sucursal_destino_nombre = serializers.CharField(source='sucursal_destino.nombre', read_only=True)
    creado_por_username = serializers.CharField(source='creado_por.username', read_only=True)
    cotizacion_base_numero = serializers.CharField(source='cotizacion_base.numero_cotizacion', read_only=True)
    detalles = DetalleOrdenCompraSerializer(many=True, read_only=True) # Anidamos los detalles

    class Meta:
        model = OrdenCompra
        fields = [
            'id', 'proveedor', 'proveedor_nombre', 'sucursal_destino', 'sucursal_destino_nombre',
            'cotizacion_base', 'cotizacion_base_numero', 'fecha_orden', 'fecha_entrega_estimada',
            'numero_orden', 'subtotal', 'impuestos', 'total_orden', 'estado',
            'observaciones', 'creado_por', 'creado_por_username', 'detalles'
        ]
        read_only_fields = ['subtotal', 'impuestos', 'total_orden', 'fecha_orden']

    def create(self, validated_data):
        detalles_data = validated_data.pop('detalles', [])
        orden_compra = OrdenCompra.objects.create(**validated_data)
        for detalle_data in detalles_data:
            DetalleOrdenCompra.objects.create(orden_compra=orden_compra, **detalle_data)
        orden_compra.calcular_totales()
        return orden_compra

    def update(self, instance, validated_data):
        detalles_data = validated_data.pop('detalles', [])
        instance = super().update(instance, validated_data)
        instance.calcular_totales()
        return instance

# Serializador para DetalleCompra
class DetalleCompraSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)

    class Meta:
        model = DetalleCompra
        fields = [
            'id', 'compra', 'producto', 'producto_nombre', 'cantidad_recibida',
            'precio_unitario_compra', 'lote', 'fecha_vencimiento', 'subtotal_linea'
        ]
        read_only_fields = ['subtotal_linea']

# Serializador para Compra
class CompraSerializer(serializers.ModelSerializer):
    proveedor_nombre = serializers.CharField(source='proveedor.nombre_comercial', read_only=True)
    sucursal_destino_nombre = serializers.CharField(source='sucursal_destino.nombre', read_only=True)
    orden_compra_asociada_numero = serializers.CharField(source='orden_compra_asociada.numero_orden', read_only=True)
    registrado_por_username = serializers.CharField(source='registrado_por.username', read_only=True)
    detalles = DetalleCompraSerializer(many=True, read_only=True) # Anidamos los detalles

    class Meta:
        model = Compra
        fields = [
            'id', 'proveedor', 'proveedor_nombre', 'sucursal_destino', 'sucursal_destino_nombre',
            'orden_compra_asociada', 'orden_compra_asociada_numero', 'fecha_recepcion',
            'numero_factura_proveedor', 'subtotal', 'impuestos', 'total_compra',
            'estado', 'observaciones', 'registrado_por', 'registrado_por_username', 'detalles'
        ]
        read_only_fields = ['subtotal', 'impuestos', 'total_compra', 'fecha_recepcion']

    def create(self, validated_data):
        detalles_data = validated_data.pop('detalles', [])
        compra = Compra.objects.create(**validated_data)
        for detalle_data in detalles_data:
            # Aquí, al crear DetalleCompra, podrías querer llamar a actualizar_stock_por_compra
            # pero es mejor hacerlo en el ViewSet o una acción separada para controlar el "procesamiento"
            DetalleCompra.objects.create(compra=compra, **detalle_data)
        compra.calcular_totales()
        return compra

    def update(self, instance, validated_data):
        detalles_data = validated_data.pop('detalles', [])
        instance = super().update(instance, validated_data)
        instance.calcular_totales()
        return instance

