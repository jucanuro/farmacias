# inventario/serializers.py
from rest_framework import serializers
from .models import (
    CategoriaProducto, Laboratorio, PrincipioActivo,
    FormaFarmaceutica, Producto, StockProducto, MovimientoInventario
)
from core.serializers import SucursalSerializer # Importamos para anidar el serializador de Sucursal


# Serializador para CategoriaProducto
class CategoriaProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaProducto
        fields = ['id', 'nombre', 'descripcion']

# Serializador para Laboratorio
class LaboratorioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Laboratorio
        fields = ['id', 'nombre', 'direccion', 'telefono', 'email']

# Serializador para PrincipioActivo
class PrincipioActivoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrincipioActivo
        fields = ['id', 'nombre', 'descripcion']

# Serializador para FormaFarmaceutica
class FormaFarmaceuticaSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormaFarmaceutica
        fields = ['id', 'nombre', 'descripcion']

# Serializador para Producto
class ProductoSerializer(serializers.ModelSerializer):
    # Campos de solo lectura para mostrar nombres de relaciones
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    laboratorio_nombre = serializers.CharField(source='laboratorio.nombre', read_only=True)
    principio_activo_nombre = serializers.CharField(source='principio_activo.nombre', read_only=True)
    forma_farmaceutica_nombre = serializers.CharField(source='forma_farmaceutica.nombre', read_only=True)
    # Campo calculado para el precio de venta sugerido
    precio_venta_sugerido = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True, source='get_precio_venta_sugerido'
    )

    class Meta:
        model = Producto
        fields = [
            'id', 'nombre', 'descripcion', 'codigo_barras',
            'principio_activo', 'principio_activo_nombre',
            'concentracion', 'forma_farmaceutica', 'forma_farmaceutica_nombre',
            'laboratorio', 'laboratorio_nombre', 'categoria', 'categoria_nombre',
            'presentacion_base', 'cantidad_por_presentacion_base', 'unidad_medida',
            'precio_compra_promedio', 'margen_ganancia_sugerido', 'precio_venta_sugerido',
            'aplica_receta', 'es_controlado', 'imagen_producto', 'fecha_registro'
        ]
        read_only_fields = ['fecha_registro', 'precio_venta_sugerido']

# Serializador para StockProducto
class StockProductoSerializer(serializers.ModelSerializer):
    # Anidar serializadores para mostrar detalles de Producto y Sucursal
    producto_data = ProductoSerializer(source='producto', read_only=True)
    sucursal_data = SucursalSerializer(source='sucursal', read_only=True)
    # Puedes añadir un campo para el nombre del producto si solo necesitas eso
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    sucursal_nombre = serializers.CharField(source='sucursal.nombre', read_only=True)

    class Meta:
        model = StockProducto
        fields = [
            'id', 'producto', 'producto_data', 'producto_nombre',
            'sucursal', 'sucursal_data', 'sucursal_nombre',
            'lote', 'fecha_vencimiento', 'cantidad', 'ubicacion_almacen', 'ultima_actualizacion'
        ]
        read_only_fields = ['ultima_actualizacion']

# Serializador para MovimientoInventario
class MovimientoInventarioSerializer(serializers.ModelSerializer):
    # Anidar serializadores o mostrar nombres para mejor legibilidad
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    sucursal_nombre = serializers.CharField(source='sucursal.nombre', read_only=True)
    usuario_username = serializers.CharField(source='usuario.username', read_only=True)
    stock_producto_lote = serializers.CharField(source='stock_afectado.lote', read_only=True)

    class Meta:
        model = MovimientoInventario
        fields = [
            'id', 'producto', 'producto_nombre',
            'sucursal', 'sucursal_nombre',
            'stock_afectado', 'stock_producto_lote', # Referencia al ID y lote del stock afectado
            'tipo_movimiento', 'cantidad', 'fecha_movimiento',
            'usuario', 'usuario_username', 'referencia_doc', 'observaciones'
        ]
        read_only_fields = ['fecha_movimiento']

