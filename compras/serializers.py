from django.db import transaction
from rest_framework import serializers
from .models import (
    CotizacionProveedor, DetalleCotizacion,
    OrdenCompra, DetalleOrdenCompra,
    Compra, DetalleCompra
)
# Nota: Las siguientes importaciones asumen que ya tienes estos serializers
# en sus respectivas apps. Si no, puedes comentarlas por ahora.
# from proveedores.serializers import ProveedorSerializer
# from inventario.serializers import ProductoSerializer
# from core.serializers import SucursalSerializer, UsuarioSerializer


# --- Serializador para DetalleCompra (para poder escribirlo anidado) ---
class DetalleCompraSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    
    class Meta:
        model = DetalleCompra
        fields = [
            'id', 'compra', 'producto', 'producto_nombre', 'cantidad_recibida',
            'precio_unitario_compra', 'lote', 'fecha_vencimiento', 'subtotal_linea','presentacion',
        ]


class DetalleCompraWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleCompra
        fields = [
            'compra',
            'producto', 
            'cantidad_recibida', 
            'precio_unitario_compra', 
            'lote', 
            'fecha_vencimiento',
            'presentacion'
        ]

# --- Serializador Principal para Compra (Creación y Lectura) ---
class CompraSerializer(serializers.ModelSerializer):
    # En esta línea, cambiamos 'write_only=True' por dos nuevos parámetros
    detalles = DetalleCompraSerializer(many=True, read_only=True)
    
    # ... el resto del serializer se queda igual ...
    proveedor_nombre = serializers.CharField(source='proveedor.nombre_comercial', read_only=True)
    sucursal_destino_nombre = serializers.CharField(source='sucursal_destino.nombre', read_only=True)
    registrado_por_username = serializers.CharField(source='registrado_por.username', read_only=True)

    class Meta:
        model = Compra
        fields = '__all__'
        read_only_fields = ['registrado_por', 'subtotal', 'impuestos', 'total_compra', 'fecha_recepcion']
    
    def create(self, validated_data):
        """
        Versión corregida y simplificada.
        'registrado_por' ya viene en validated_data gracias al ViewSet.
        """
        detalles_data = validated_data.pop('detalles', [])

        with transaction.atomic():
            # Simplemente creamos la compra con los datos validados.
            # El estado 'PENDIENTE' puede ser un valor por defecto en el modelo.
            compra = Compra.objects.create(estado='PENDIENTE', **validated_data)

            if detalles_data:
                for detalle_data in detalles_data:
                    DetalleCompra.objects.create(compra=compra, **detalle_data)
                compra.calcular_totales()
        
        return compra

# --- Serializadores Adicionales (Configurados como solo lectura para simplificar) ---

class DetalleCotizacionSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    class Meta:
        model = DetalleCotizacion
        fields = ['id', 'producto', 'producto_nombre', 'cantidad', 'precio_unitario_cotizado', 'subtotal_linea']

class CotizacionProveedorSerializer(serializers.ModelSerializer):
    detalles = DetalleCotizacionSerializer(many=True, read_only=True)
    proveedor_nombre = serializers.CharField(source='proveedor.nombre_comercial', read_only=True)
    class Meta:
        model = CotizacionProveedor
        fields = '__all__'

class DetalleOrdenCompraSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    class Meta:
        model = DetalleOrdenCompra
        fields = ['id', 'producto', 'producto_nombre', 'cantidad_solicitada', 'cantidad_recibida', 'precio_unitario_oc', 'subtotal_linea']

class OrdenCompraSerializer(serializers.ModelSerializer):
    detalles = DetalleOrdenCompraSerializer(many=True, read_only=True)
    proveedor_nombre = serializers.CharField(source='proveedor.nombre_comercial', read_only=True)
    sucursal_destino_nombre = serializers.CharField(source='sucursal_destino.nombre', read_only=True)
    class Meta:
        model = OrdenCompra
        fields = '__all__'