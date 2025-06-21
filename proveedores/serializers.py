# proveedores/serializers.py
from rest_framework import serializers
from .models import Proveedor

class ProveedorSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo Proveedor.
    Permite serializar/deserializar los datos del proveedor.
    """
    class Meta:
        model = Proveedor
        fields = [
            'id', 'nombre_comercial', 'razon_social', 'tipo_documento',
            'numero_documento', 'direccion', 'telefono', 'email',
            'sitio_web', 'persona_contacto', 'telefono_contacto',
            'condiciones_pago', 'activo', 'fecha_registro'
        ]
        read_only_fields = ['fecha_registro']
