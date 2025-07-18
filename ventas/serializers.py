# ventas/serializers.py
from rest_framework import serializers
from .models import Venta, DetalleVenta, SesionCaja
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
    cliente_telefono = serializers.CharField(source='cliente.telefono', read_only=True, allow_null=True)

    
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
            'detalles', # Detalles para la creación anidada
            'cliente_telefono',
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
        # 1. Extraemos los datos de los detalles PRIMERO.
        # Esto deja el diccionario 'validated_data' limpio para crear la Venta.
        detalles_data = validated_data.pop('detalles')
        
        # 2. Obtenemos el usuario y su sesión de caja activa desde el contexto.
        usuario_actual = self.context['request'].user
        sesion_activa = SesionCaja.objects.filter(usuario=usuario_actual, estado='ABIERTA').first()

        if not sesion_activa:
            raise serializers.ValidationError("No hay una sesión de caja abierta para este usuario.")

        # 3. Añadimos los datos del vendedor y la sesión al diccionario principal.
        validated_data['vendedor'] = usuario_actual
        validated_data['sesion_caja'] = sesion_activa
        validated_data['estado'] = 'COMPLETADA'
        
        # 4. Creamos la Venta principal con los datos ya limpios (SIN 'detalles').
        # Eliminamos el try/except y la creación duplicada.
        venta = Venta.objects.create(**validated_data)
        
        # 5. Creamos cada DetalleVenta, asociándolo a la Venta recién creada.
        for detalle_data in detalles_data:
            DetalleVenta.objects.create(venta=venta, **detalle_data)
        
        # El método save() de cada DetalleVenta ya llama a venta.actualizar_totales(),
        # por lo que al final de este bucle, la venta ya tiene sus totales correctos.
        # No es necesario llamar a venta.actualizar_totales() aquí de nuevo.
        
        # 6. Devolvemos la instancia de la venta creada y actualizada.
        return venta
    
    def update(self, instance, validated_data):
        validated_data.pop('detalles', None)
        instance = super().update(instance, validated_data)
        instance.calcular_totales()
        return instance

class SesionCajaSerializer(serializers.ModelSerializer):
    """ Serializador para el modelo SesionCaja. """
    # Mostramos el nombre del usuario para mayor claridad en la respuesta de la API
    usuario_username = serializers.CharField(source='usuario.username', read_only=True)
    sucursal_nombre = serializers.CharField(source='sucursal.nombre', read_only=True)

    class Meta:
        model = SesionCaja
        fields = '__all__'
        read_only_fields = (
            'usuario', 'sucursal', 'monto_final_sistema', 'diferencia', 
            'fecha_apertura', 'fecha_cierre', 'estado'
        )