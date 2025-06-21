# clientes/serializers.py
from rest_framework import serializers
from .models import Cliente
from core.serializers import FarmaciaSerializer # Importamos para anidar el serializador de Farmacia

class ClienteSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo Cliente.
    Permite serializar/deserializar los datos del cliente,
    incluyendo el nombre de la farmacia asociada (si aplica).
    """
    farmacia_nombre = serializers.CharField(source='farmacia.nombre', read_only=True)

    class Meta:
        model = Cliente
        fields = [
            'id', 'farmacia', 'farmacia_nombre',
            'tipo_documento', 'numero_documento',
            'nombres', 'apellidos', 'direccion', 'telefono', 'email',
            'fecha_nacimiento', 'fecha_registro', 'activo'
        ]
        read_only_fields = ['fecha_registro']
        # Para asegurar que el número de documento sea único globalmente
        # O podrías definir una validación personalizada más compleja si la unicidad
        # depende del tipo de documento o farmacia.
        extra_kwargs = {
            'numero_documento': {'validators': []}, # Remover validator default si quieres customizar
        }

    # Puedes agregar validaciones personalizadas aquí si es necesario
    def validate(self, data):
        """
        Valida que el número de documento sea único para la combinación
        de tipo_documento y número_documento.
        """
        # Para actualizaciones, excluye la propia instancia del cliente de la verificación de unicidad
        instance = self.instance
        if instance:
            # En caso de actualización, el numero_documento puede no cambiar
            if data.get('numero_documento') == instance.numero_documento and \
               data.get('tipo_documento') == instance.tipo_documento:
                return data

        # Verificar unicidad de tipo_documento + numero_documento
        qs = Cliente.objects.filter(
            tipo_documento=data.get('tipo_documento'),
            numero_documento=data.get('numero_documento')
        )
        if instance:
            qs = qs.exclude(pk=instance.pk) # Excluye la instancia actual en caso de actualización

        if qs.exists():
            raise serializers.ValidationError(
                "Ya existe un cliente con este tipo y número de documento."
            )
        return data

