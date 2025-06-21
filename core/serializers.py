# core/serializers.py
from rest_framework import serializers
from .models import Farmacia, Sucursal, Rol, Usuario, ConfiguracionFacturacionElectronica

# Serializador para el modelo Rol
class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = ['id', 'nombre', 'descripcion'] # Los campos que queremos exponer en la API

# Serializador para el modelo de usuario (Usuario)
class UsuarioSerializer(serializers.ModelSerializer):
    # Para mostrar los nombres de las relaciones en lugar de solo los IDs
    farmacia_nombre = serializers.CharField(source='farmacia.nombre', read_only=True)
    sucursal_nombre = serializers.CharField(source='sucursal.nombre', read_only=True)
    rol_nombre = serializers.CharField(source='rol.nombre', read_only=True)

    class Meta:
        model = Usuario
        # Exponemos solo los campos que son seguros y relevantes para la API.
        # Nunca expongas la contraseña directamente.
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'farmacia', 'farmacia_nombre',
            'sucursal', 'sucursal_nombre',
            'rol', 'rol_nombre',
            'is_staff', 'is_active', 'date_joined'
        ]
        read_only_fields = ['username', 'is_staff', 'is_active', 'date_joined', 'farmacia_nombre', 'sucursal_nombre', 'rol_nombre']

    # Método para manejar la creación y actualización de usuarios
    # Si no se define, DRF usa el comportamiento por defecto de ModelSerializer
    # def create(self, validated_data):
    #     user = Usuario.objects.create_user(**validated_data)
    #     return user

    # def update(self, instance, validated_data):
    #     instance.username = validated_data.get('username', instance.username)
    #     instance.email = validated_data.get('email', instance.email)
    #     # ... otros campos
    #     instance.save()
    #     return instance


# Serializador para la configuración de Facturación Electrónica
class ConfiguracionFacturacionElectronicaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfiguracionFacturacionElectronica
        fields = [
            'id', 'api_key', 'api_secret', 'url_base_api', 'certificado_pem',
            'clave_certificado', 'modo_produccion', 'ruc_emisor', 'nombre_emisor'
        ]
        # Puedes hacer que campos sensibles sean de solo escritura al actualizar
        extra_kwargs = {
            'api_key': {'write_only': True},
            'api_secret': {'write_only': True},
            'certificado_pem': {'write_only': True},
            'clave_certificado': {'write_only': True},
        }

# Serializador para el modelo Farmacia
class FarmaciaSerializer(serializers.ModelSerializer):
    # Incluir la configuración de FE de solo lectura
    configuracion_facturacion_electronica_data = ConfiguracionFacturacionElectronicaSerializer(
        source='configuracion_facturacion_electronica', read_only=True
    )
    # Opcional: Para ver un conteo de sucursales
    sucursales_count = serializers.IntegerField(source='sucursales.count', read_only=True)

    class Meta:
        model = Farmacia
        fields = [
            'id', 'nombre', 'razon_social', 'ruc', 'direccion', 'telefono', 'email',
            'logo', 'configuracion_facturacion_electronica',
            'configuracion_facturacion_electronica_data', 'fecha_registro',
            'sucursales_count'
        ]
        read_only_fields = ['fecha_registro', 'sucursales_count']


# Serializador para el modelo Sucursal
class SucursalSerializer(serializers.ModelSerializer):
    # Para mostrar el nombre de la farmacia y el administrador
    farmacia_nombre = serializers.CharField(source='farmacia.nombre', read_only=True)
    administrador_username = serializers.CharField(source='administrador.username', read_only=True)

    class Meta:
        model = Sucursal
        fields = [
            'id', 'farmacia', 'farmacia_nombre', 'nombre', 'codigo', 'direccion',
            'telefono', 'administrador', 'administrador_username', 'fecha_apertura'
        ]
        read_only_fields = ['fecha_apertura']

