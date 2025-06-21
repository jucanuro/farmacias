# core/api_views.py
from rest_framework import viewsets, permissions
from .models import Farmacia, Sucursal, Rol, Usuario, ConfiguracionFacturacionElectronica
from .serializers import (
    FarmaciaSerializer, SucursalSerializer, RolSerializer,
    UsuarioSerializer, ConfiguracionFacturacionElectronicaSerializer
)

# ViewSet para el modelo Rol
class RolViewSet(viewsets.ModelViewSet):
    """
    API endpoint que permite a los Roles ser vistos o editados.
    """
    queryset = Rol.objects.all().order_by('nombre')
    serializer_class = RolSerializer
    permission_classes = [permissions.IsAuthenticated] # Solo usuarios autenticados pueden acceder

# ViewSet para el modelo Usuario
class UsuarioViewSet(viewsets.ModelViewSet):
    """
    API endpoint que permite a los Usuarios ser vistos o editados.
    Nota: Se debe tener cuidado al exponer este endpoint.
    """
    queryset = Usuario.objects.all().order_by('username')
    serializer_class = UsuarioSerializer
    permission_classes = [permissions.IsAdminUser] # Solo administradores pueden gestionar usuarios

    # Opcional: Sobreescribir perform_create para encriptar la contraseña si se recibe en la creación
    def perform_create(self, serializer):
        if 'password' in self.request.data:
            password = self.request.data['password']
            user = serializer.save()
            user.set_password(password) # Encripta la contraseña
            user.save()
        else:
            serializer.save()

    # Opcional: Sobreescribir perform_update para encriptar la contraseña si se recibe en la actualización
    def perform_update(self, serializer):
        if 'password' in self.request.data and self.request.data['password']:
            password = self.request.data['password']
            user = serializer.save()
            user.set_password(password)
            user.save()
        else:
            serializer.save()


# ViewSet para ConfiguracionFacturacionElectronica
class ConfiguracionFacturacionElectronicaViewSet(viewsets.ModelViewSet):
    """
    API endpoint que permite a las Configuraciones de FE ser vistas o editadas.
    """
    queryset = ConfiguracionFacturacionElectronica.objects.all()
    serializer_class = ConfiguracionFacturacionElectronicaSerializer
    permission_classes = [permissions.IsAdminUser] # Solo administradores pueden gestionar configuraciones sensibles


# ViewSet para el modelo Farmacia
class FarmaciaViewSet(viewsets.ModelViewSet):
    """
    API endpoint que permite a las Farmacias ser vistas o editadas.
    """
    queryset = Farmacia.objects.all().order_by('nombre')
    serializer_class = FarmaciaSerializer
    # Permite a cualquier usuario autenticado ver farmacias, pero solo admins crearlas/editarlas
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]


# ViewSet para el modelo Sucursal
class SucursalViewSet(viewsets.ModelViewSet):
    """
    API endpoint que permite a las Sucursales ser vistas o editadas.
    """
    queryset = Sucursal.objects.all().order_by('nombre')
    serializer_class = SucursalSerializer
    # Permite a cualquier usuario autenticado ver sucursales, pero solo admins crearlas/editarlas
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]

