from rest_framework import serializers
from .models import Farmacia, Sucursal, Rol, Usuario, ConfiguracionFacturacionElectronica


class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = ['id', 'nombre', 'descripcion']


class UsuarioSerializer(serializers.ModelSerializer):
    farmacia_nombre = serializers.CharField(source='farmacia.nombre', read_only=True)
    sucursal_nombre = serializers.CharField(source='sucursal.nombre', read_only=True)
    rol_nombre = serializers.CharField(source='rol.nombre', read_only=True)

    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'farmacia', 'farmacia_nombre',
            'sucursal', 'sucursal_nombre',
            'rol', 'rol_nombre',
            'is_staff', 'is_active', 'date_joined'
        ]
        read_only_fields = [
            'username',
            'is_staff',
            'is_active',
            'date_joined',
            'farmacia_nombre',
            'sucursal_nombre',
            'rol_nombre'
        ]


class ConfiguracionFacturacionElectronicaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfiguracionFacturacionElectronica
        fields = [
            'id', 'api_key', 'api_secret', 'url_base_api', 'certificado_pem',
            'clave_certificado', 'modo_produccion', 'ruc_emisor', 'nombre_emisor'
        ]
        extra_kwargs = {
            'api_key': {'write_only': True},
            'api_secret': {'write_only': True},
            'certificado_pem': {'write_only': True},
            'clave_certificado': {'write_only': True},
        }


class FarmaciaSerializer(serializers.ModelSerializer):
    configuracion_facturacion_electronica_data = ConfiguracionFacturacionElectronicaSerializer(
        source='configuracion_facturacion_electronica',
        read_only=True
    )
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


class SucursalSerializer(serializers.ModelSerializer):
    farmacia_nombre = serializers.CharField(source='farmacia.nombre', read_only=True)
    administrador_username = serializers.CharField(source='administrador.username', read_only=True)

    class Meta:
        model = Sucursal
        fields = [
            'id', 'farmacia', 'farmacia_nombre', 'nombre', 'codigo', 'direccion',
            'telefono', 'administrador', 'administrador_username', 'fecha_apertura'
        ]
        read_only_fields = ['fecha_apertura']