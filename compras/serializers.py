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
class DetalleCompraWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleCompra
        fields = [
            'producto', 
            'cantidad_recibida', 
            'precio_unitario_compra', 
            'lote', 
            'fecha_vencimiento'
        ]

# --- Serializador Principal para Compra (Creación y Lectura) ---
class CompraSerializer(serializers.ModelSerializer):
    detalles = DetalleCompraWriteSerializer(many=True, write_only=True)
    proveedor_nombre = serializers.CharField(source='proveedor.nombre_comercial', read_only=True)
    sucursal_destino_nombre = serializers.CharField(source='sucursal_destino.nombre', read_only=True)
    registrado_por_username = serializers.CharField(source='registrado_por.username', read_only=True)

    class Meta:
        model = Compra
        fields = [
            'id', 'proveedor', 'sucursal_destino', 'numero_factura_proveedor', 
            'observaciones', 'estado', 'detalles', 
            'proveedor_nombre', 'sucursal_destino_nombre', 
            'registrado_por', # <-- Añadimos 'registrado_por' para que esté en los campos de lectura
            'registrado_por_username', 
            'fecha_recepcion', 'subtotal', 'impuestos', 'total_compra'
        ]
        # --- CORRECCIÓN CLAVE AQUÍ ---
        # Le decimos a DRF que 'registrado_por' no debe venir del cliente,
        # sino que se asignará en el servidor.
        read_only_fields = ['registrado_por']
    
    def create(self, validated_data):
        detalles_data = validated_data.pop('detalles')
        usuario = self.context['request'].user

        with transaction.atomic():
            # Creamos la compra. 'registrado_por' ya no viene en validated_data.
            compra = Compra.objects.create(registrado_por=usuario, estado='PROCESADA', **validated_data)

            for detalle_data in detalles_data:
                detalle = DetalleCompra.objects.create(compra=compra, **detalle_data)
                detalle.actualizar_stock_por_compra(usuario_accion=usuario)
            
            compra.calcular_totales()
        
        return compra
# --- Serializador Estándar para DetalleCompra (AÑADIDO) ---
class DetalleCompraSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    
    class Meta:
        model = DetalleCompra
        fields = [
            'id', 'compra', 'producto', 'producto_nombre', 'cantidad_recibida',
            'precio_unitario_compra', 'lote', 'fecha_vencimiento', 'subtotal_linea'
        ]


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