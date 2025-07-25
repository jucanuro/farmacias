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
    Serializador para el modelo Producto adaptado al modelo SaaS.
    Busca el precio de venta local en el stock de la sucursal actual y, 
    si no existe, usa el precio sugerido global para calcular los precios.
    """
    laboratorio_nombre = serializers.CharField(source='laboratorio.nombre', read_only=True)
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)

    # El campo que contendrá el diccionario de precios (caja, blister, unidad)
    precios = serializers.SerializerMethodField()
    precio_venta = serializers.SerializerMethodField()

    class Meta:
        model = Producto
        # Eliminamos 'precio_venta' porque ahora se maneja en el campo 'precios'
        fields = [
            'id', 'nombre', 'concentracion', 'laboratorio_nombre', 'categoria_nombre',
            'imagen_producto',
            'unidades_por_caja',
            'unidades_por_blister',
            'precios', # Nuestro campo con todos los precios calculados
            'precio_venta'
        ]

    def get_precios(self, producto):
        request = self.context.get('request')
        
        # 1. El precio base ahora es el PRECIO UNITARIO.
        #    Lo tomamos del stock local o, si no existe, del precio sugerido.
        precio_base_unidad = producto.precio_venta_sugerido

        if request and hasattr(request.user, 'sucursal') and request.user.sucursal:
            stock_local = StockProducto.objects.filter(
                producto=producto,
                sucursal=request.user.sucursal
            ).first()
            if stock_local and stock_local.precio_venta > 0:
                # El precio de venta del stock local AHORA es el precio unitario.
                precio_base_unidad = stock_local.precio_venta
        
        # 2. Asignamos el precio por unidad.
        precio_unidad = Decimal(precio_base_unidad or '0.0')

        # 3. Calculamos HACIA ARRIBA para el blíster y la caja.
        precio_blister = Decimal('0.0')
        if producto.unidades_por_blister > 0:
            precio_blister = precio_unidad * Decimal(producto.unidades_por_blister)

        precio_caja = Decimal('0.0')
        if producto.unidades_por_caja > 0:
             # El precio de la caja es el precio unitario por el total de unidades.
             precio_caja = precio_unidad * Decimal(producto.unidades_por_caja)

        return {
            'caja': float(precio_caja),
            'blister': float(precio_blister),
            'unidad': float(precio_unidad)
        }
    
    def get_precio_venta(self, producto):
        """
        Reutiliza la lógica de get_precios para devolver solo el precio unitario.
        """
        precios_dict = self.get_precios(producto)
        return precios_dict.get('unidad', 0.0)
        
class StockProductoSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)

    # ... (tu serializer de stock)
    class Meta:
        model = StockProducto
        fields = '__all__'

class MovimientoInventarioSerializer(serializers.ModelSerializer):
    # ... (tu serializer de movimientos)
    class Meta:
        model = MovimientoInventario
        fields = '__all__'