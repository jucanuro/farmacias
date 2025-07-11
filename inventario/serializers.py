from rest_framework import serializers
from decimal import Decimal, ROUND_UP
from .models import (
    CategoriaProducto, Laboratorio, PrincipioActivo,
    FormaFarmaceutica, UnidadPresentacion, Producto, 
    StockProducto, MovimientoInventario
)
# from core.serializers import SucursalSerializer 


# --- Serializers de Datos Maestros (sin cambios) ---
class CategoriaProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaProducto
        fields = ['id', 'nombre', 'descripcion']

class LaboratorioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Laboratorio
        fields = ['id', 'nombre', 'direccion', 'telefono', 'email']

class PrincipioActivoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrincipioActivo
        fields = ['id', 'nombre', 'descripcion']

class FormaFarmaceuticaSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormaFarmaceutica
        fields = ['id', 'nombre', 'descripcion']

# --- NUEVO SERIALIZER PARA LA JERARQUÍA DE UNIDADES ---
class UnidadJerarquiaSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    nombre = serializers.CharField()
    factor_conversion_a_base = serializers.IntegerField()


# --- SERIALIZER DE AUTOCOMPLETADO (ACTUALIZADO) ---
class ProductoAutocompleteSerializer(serializers.ModelSerializer):
    laboratorio_nombre = serializers.CharField(source='laboratorio.nombre', read_only=True)
    unidades_jerarquia = UnidadJerarquiaSerializer(source='get_unidades_compra_jerarquia', many=True, read_only=True)
    
    class Meta:
        model = Producto
        fields = [
            'id', 
            'nombre', 
            'concentracion', 
            'laboratorio_nombre',
            'unidad_venta', # ID de la unidad base para el stock
            'unidades_jerarquia' # La lista de unidades de compra posibles
        ]

# --- OTROS SERIALIZERS (sin cambios) ---
class ProductoSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo Producto.
    Calcula y añade una estructura de precios para diferentes unidades de venta.
    """
    # Campos de solo lectura para mostrar nombres en lugar de IDs
    laboratorio_nombre = serializers.CharField(source='laboratorio.nombre', read_only=True)
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)

    # --- CAMPO CLAVE: Se añade un campo personalizado para los precios ---
    precios = serializers.SerializerMethodField()

    class Meta:
        model = Producto
        # Asegúrate de incluir todos los campos que la interfaz necesita
        fields = [
            'id', 'nombre', 'concentracion', 'laboratorio_nombre', 'categoria_nombre',
            'imagen_producto',
            'precio_venta', # Precio base (caja)
            'unidades_por_caja',
            'unidades_por_blister',
            'precios' # Nuestro nuevo campo con todos los precios calculados
        ]

    def get_precios(self, obj):
        """
        Este método se ejecuta para cada producto y calcula los precios.
        'obj' es la instancia del producto que se está serializando.
        """
        # El precio de venta guardado se asume que es el de la caja
        precio_caja = obj.precio_venta or Decimal('0.0')
        
        # 1. Calcular el precio por unidad básica (pastilla, cápsula, etc.)
        precio_unidad = Decimal('0.0')
        if obj.unidades_por_caja > 0:
            # Dividimos el precio de la caja entre las unidades que contiene
            # y redondeamos hacia arriba al céntimo más cercano (práctica comercial común)
            precio_unidad = (precio_caja / Decimal(obj.unidades_por_caja)).quantize(
                Decimal('0.01'), rounding=ROUND_UP
            )
        
        # 2. Calcular el precio por blíster
        precio_blister = Decimal('0.0')
        if obj.unidades_por_blister > 0:
            # Multiplicamos el precio unitario por la cantidad de unidades en un blíster
            precio_blister = precio_unidad * Decimal(obj.unidades_por_blister)

        # 3. Devolvemos un diccionario limpio para que el frontend lo use
        return {
            'caja': float(precio_caja),
            'blister': float(precio_blister),
            'unidad': float(precio_unidad)
        }

class StockProductoSerializer(serializers.ModelSerializer):
    # ... (tu serializer de stock)
    class Meta:
        model = StockProducto
        fields = '__all__'

class MovimientoInventarioSerializer(serializers.ModelSerializer):
    # ... (tu serializer de movimientos)
    class Meta:
        model = MovimientoInventario
        fields = '__all__'