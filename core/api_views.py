from rest_framework import viewsets, permissions
from .models import Farmacia, Sucursal, Rol, Usuario, ConfiguracionFacturacionElectronica
from .serializers import (
    FarmaciaSerializer, SucursalSerializer, RolSerializer,
    UsuarioSerializer, ConfiguracionFacturacionElectronicaSerializer
)


class RolViewSet(viewsets.ModelViewSet):
    queryset = Rol.objects.all().order_by('nombre')
    serializer_class = RolSerializer
    permission_classes = [permissions.IsAuthenticated]


class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all().order_by('username')
    serializer_class = UsuarioSerializer
    permission_classes = [permissions.IsAdminUser]

    def perform_create(self, serializer):
        if 'password' in self.request.data:
            password = self.request.data['password']
            user = serializer.save()
            user.set_password(password)
            user.save()
        else:
            serializer.save()

    def perform_update(self, serializer):
        if 'password' in self.request.data and self.request.data['password']:
            password = self.request.data['password']
            user = serializer.save()
            user.set_password(password)
            user.save()
        else:
            serializer.save()


class ConfiguracionFacturacionElectronicaViewSet(viewsets.ModelViewSet):
    queryset = ConfiguracionFacturacionElectronica.objects.all()
    serializer_class = ConfiguracionFacturacionElectronicaSerializer
    permission_classes = [permissions.IsAdminUser]


class FarmaciaViewSet(viewsets.ModelViewSet):
    queryset = Farmacia.objects.all().order_by('nombre')
    serializer_class = FarmaciaSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]


class SucursalViewSet(viewsets.ModelViewSet):
    queryset = Sucursal.objects.all().order_by('nombre')
    serializer_class = SucursalSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]