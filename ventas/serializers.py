# ventas/serializers.py
from rest_framework import serializers
from .models import Venta, DetalleVenta
from core.serializers import SucursalSerializer, UsuarioSerializer # Importamos para anidamiento
from clientes.serializers import ClienteSerializer # Importamos para anidamiento
from inventario.serializers import ProductoSerializer, StockProductoSerializer # Importamos para anidamiento

# Serializador para DetalleVenta
class DetalleVentaSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True, default='')

    class Meta:
        model = DetalleVenta
        fields = [
            'id', 'venta', 'producto', 'producto_nombre',
            'stock_producto',
            'cantidad', 'unidad_venta', 'precio_unitario',
            'monto_descuento_linea', # <-- CORREGIDO de 'descuento_linea'
            'subtotal_linea'
        ]
        read_only_fields = ['subtotal_linea']
        # Hacemos que el campo 'venta' no sea requerido al crear un detalle
        # porque lo asignaremos desde el ViewSet o la lógica de creación anidada.
        extra_kwargs = {'venta': {'required': False, 'allow_null': True}}

# Serializador para Venta
class VentaSerializer(serializers.ModelSerializer):
    # Campos de solo lectura para mostrar nombres en lugar de IDs
    sucursal_nombre = serializers.CharField(source='sucursal.nombre', read_only=True)
    cliente_nombre_completo = serializers.CharField(source='cliente.get_full_name', read_only=True, default='')
    vendedor_username = serializers.CharField(source='vendedor.username', read_only=True)
    
    # Para permitir la creación de la venta con sus detalles en una sola petición
    detalles = DetalleVentaSerializer(many=True)

    class Meta:
        model = Venta
        # Se incluyen TODOS los campos del modelo Venta, incluyendo los nuevos
        fields = [
            'id', 'sucursal', 'sucursal_nombre',
            'cliente', 'cliente_nombre_completo',
            'vendedor', 'vendedor_username', 'fecha_venta',
            'tipo_comprobante', 'numero_comprobante', 
            'subtotal', 'impuestos', 'monto_descuento', # <-- CORREGIDO de 'descuento_total'
            'total_venta', 
            'metodo_pago', 'monto_recibido', 'vuelto', # <-- NUEVOS campos de pago
            'qr_code_data', 'estado', # <-- NUEVOS campos de estado y QR
            'estado_facturacion_electronica', 'uuid_comprobante_fe', 'observaciones_fe',
            'detalles' # Detalles para la creación anidada
        ]
        read_only_fields = [
            'fecha_venta', 'vendedor', 'sucursal', 
            'total_venta', 'subtotal', 'impuestos',
            'monto_descuento', # <-- CORREGIDO de 'descuento_total'
            'vuelto',
            'estado_facturacion_electronica',
            'uuid_comprobante_fe'
        ]

    def create(self, validated_data):
        # Extraemos los datos de los detalles
        detalles_data = validated_data.pop('detalles')
        
        # Creamos la instancia de la Venta principal
        venta = Venta.objects.create(**validated_data)
        
        # Creamos cada DetalleVenta y lo asociamos a la Venta
        for detalle_data in detalles_data:
            DetalleVenta.objects.create(venta=venta, **detalle_data)
        
        # El método save() de DetalleVenta ya llama a calcular_totales(),
        # por lo que no es estrictamente necesario llamarlo aquí de nuevo, pero no hace daño.
        venta.calcular_totales()
        return venta

    def update(self, instance, validated_data):
        # La lógica de actualización de detalles anidados puede ser compleja.
        # Por ahora, esta actualización se centrará en los campos de la Venta principal.
        validated_data.pop('detalles', None)
        instance = super().update(instance, validated_data)
        instance.calcular_totales()
        return instance

