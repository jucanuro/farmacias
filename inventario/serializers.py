from rest_framework import serializers
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
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    # ... (resto de tu serializer de producto)
    class Meta:
        model = Producto
        fields = '__all__' # Asumiendo que quieres todos los campos

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