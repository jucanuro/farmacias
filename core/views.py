# core/api_views.py
from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Farmacia, Sucursal, Rol, Usuario, ConfiguracionFacturacionElectronica
from .serializers import (
    FarmaciaSerializer, SucursalSerializer, RolSerializer,
    UsuarioSerializer, ConfiguracionFacturacionElectronicaSerializer
)
from core.permissions import IsAdminOrManager, IsAdminOrSelf, IsAdminOrSucursalManager # <-- Importar los nuevos permisos

class FarmaciaViewSet(viewsets.ModelViewSet):
    """
    API endpoint que permite a las Farmacias ser vistas o editadas.
    Solo administradores y gerentes de sucursal (para ver) tienen acceso.
    """
    queryset = Farmacia.objects.all().order_by('nombre')
    serializer_class = FarmaciaSerializer
    # Permiso: Solo Administradores o Gerentes de Sucursal pueden listar/crear.
    # Los gerentes de sucursal solo verán las farmacias a las que tienen acceso.
    permission_classes = [IsAdminOrManager]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['nombre', 'ruc']
    search_fields = ['nombre', 'ruc', 'razon_social']
    ordering_fields = ['nombre', 'ruc']

    def get_queryset(self):
        # Filtrar farmacias si el usuario no es superusuario o administrador general.
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_authenticated and not user.is_superuser and user.rol and user.rol.nombre != 'Administrador':
            # Si el usuario tiene una farmacia asociada, solo ve esa farmacia.
            if user.farmacia:
                queryset = queryset.filter(id=user.farmacia.id)
            else:
                # Si no es admin y no tiene farmacia, no ve ninguna.
                queryset = queryset.none()
        return queryset

class SucursalViewSet(viewsets.ModelViewSet):
    """
    API endpoint que permite a las Sucursales ser vistas o editadas.
    Acceso por Administradores y Gerentes de Sucursal (solo las suyas).
    """
    queryset = Sucursal.objects.all().order_by('nombre')
    serializer_class = SucursalSerializer
    # Permiso: Solo Administradores o Gerentes de Sucursal pueden listar/crear.
    # IsAdminOrSucursalManager aplicará la lógica de objeto para restringir.
    permission_classes = [IsAdminOrSucursalManager]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['farmacia', 'nombre', 'codigo']
    search_fields = ['nombre', 'codigo', 'farmacia__nombre', 'administrador__username']
    ordering_fields = ['nombre', 'farmacia']

    def get_queryset(self):
        # Filtrar sucursales por la farmacia del usuario o la sucursal administrada.
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_authenticated and not user.is_superuser and user.rol and user.rol.nombre != 'Administrador':
            if user.rol.nombre == 'Gerente de Sucursal' and user.sucursal:
                queryset = queryset.filter(id=user.sucursal.id)
            elif user.farmacia: # Si es un usuario general de una farmacia, ve todas las de su farmacia
                queryset = queryset.filter(farmacia=user.farmacia)
            else:
                queryset = queryset.none() # Si no tiene rol o asociación, no ve nada.
        return queryset


class RolViewSet(viewsets.ReadOnlyModelViewSet): # Solo lectura para los roles
    """
    API endpoint que permite a los Roles ser vistos.
    Solo administradores y gerentes de sucursal pueden ver los roles.
    """
    queryset = Rol.objects.all().order_by('nombre')
    serializer_class = RolSerializer
    permission_classes = [IsAdminOrManager] # Solo Administradores o Gerentes pueden ver roles


class UsuarioViewSet(viewsets.ModelViewSet):
    """
    API endpoint que permite a los Usuarios ser vistos o editados.
    Administradores pueden gestionar todos los usuarios.
    Los usuarios pueden ver/editar su propio perfil.
    Gerentes de Sucursal pueden ver/editar usuarios de su misma sucursal/farmacia.
    """
    queryset = Usuario.objects.all().order_by('username')
    serializer_class = UsuarioSerializer
    # Permiso: IsAuthenticated para todos los usuarios.
    # IsAdminOrSelf y IsAdminOrSucursalManager aplicarán la lógica de objeto.
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSelf, IsAdminOrSucursalManager]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_staff', 'is_active', 'farmacia', 'sucursal', 'rol']
    search_fields = ['username', 'first_name', 'last_name', 'email', 'farmacia__nombre', 'sucursal__nombre']
    ordering_fields = ['username', 'first_name', 'last_name', 'date_joined']

    def get_queryset(self):
        # Filtrar usuarios según el rol del usuario que hace la solicitud
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_authenticated:
            if user.is_superuser or (user.rol and user.rol.nombre == 'Administrador'):
                return queryset # Administradores y superusuarios ven todos los usuarios
            elif user.rol and user.rol.nombre == 'Gerente de Sucursal' and user.sucursal:
                # Los gerentes de sucursal ven los usuarios de su propia sucursal o de la misma farmacia
                # Podríamos refinar esto para solo usuarios de la misma sucursal
                return queryset.filter(sucursal__farmacia=user.sucursal.farmacia).distinct()
            else:
                # Otros usuarios solo pueden ver su propio perfil
                return queryset.filter(id=user.id)
        return queryset.none() # Si no está autenticado, no ve nada


class ConfiguracionFacturacionElectronicaViewSet(viewsets.ModelViewSet):
    """
    API endpoint que permite a las Configuraciones de Facturación Electrónica ser vistas o editadas.
    Solo administradores tienen acceso.
    """
    queryset = ConfiguracionFacturacionElectronica.objects.all()
    serializer_class = ConfiguracionFacturacionElectronicaSerializer
    permission_classes = [permissions.IsAdminUser] # Solo superusuarios y staff pueden gestionar esto.
    # Podrías crear un permiso específico si solo ciertos roles pueden acceder.

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_authenticated and not user.is_superuser and user.rol and user.rol.nombre != 'Administrador':
            # Los usuarios no administradores y no superusuarios no ven estas configuraciones.
            return queryset.none()
        return queryset

def home_view(request):
 
    return HttpResponse("<h1>¡Bienvenido al Sistema de Gestión de Farmacias!</h1><p>Esta es la página de inicio de la aplicación core.</p>")


