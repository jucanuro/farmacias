# clientes/api_views.py
from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Cliente
from .serializers import ClienteSerializer
from core.permissions import IsAdminOrManager, IsAdminOrSucursalManager # Importar permisos personalizados

class ClienteViewSet(viewsets.ModelViewSet):
    """
    API endpoint que permite a los Clientes ser vistos o editados.
    Administradores pueden gestionar todos los clientes.
    Gerentes de Sucursal y Vendedores pueden gestionar clientes de su propia farmacia.
    """
    queryset = Cliente.objects.all().order_by('apellidos', 'nombres')
    serializer_class = ClienteSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['farmacia', 'tipo_documento', 'activo']
    search_fields = [
        'nombres', 'apellidos', 'numero_documento', 'telefono', 'email',
        'farmacia__nombre'
    ]
    ordering_fields = ['apellidos', 'nombres', 'fecha_registro']

    def get_permissions(self):
        # La lógica de permisos depende de la acción y el rol del usuario.
        if self.action in ['list', 'retrieve']:
            # Todos los usuarios autenticados (Vendedores, Gerentes, Admins) pueden listar/ver clientes.
            # get_queryset restringirá lo que cada uno puede ver a su farmacia/todos.
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['create', 'update', 'partial_update']:
            # Administradores: pueden crear/editar todos.
            # Gerentes de Sucursal: pueden crear/editar clientes de su farmacia.
            # Vendedores: pueden crear/editar clientes (asociados a su farmacia).
            permission_classes = [IsAdminOrManager, permissions.IsAuthenticated] # IsAdminOrManager para admins/gerentes; IsAuthenticated para vendedores que no sean gerentes.
        elif self.action == 'destroy':
            # Solo Administradores pueden eliminar clientes. Es una acción delicada.
            permission_classes = [permissions.IsAdminUser] # IsAdminUser verifica is_staff y is_superuser
        else:
            # Por defecto, si no se especifica, requiere autenticación.
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        # Filtrar clientes según el rol y la asociación del usuario que hace la solicitud
        queryset = super().get_queryset()
        user = self.request.user

        if user.is_authenticated:
            if user.is_superuser or (user.rol and user.rol.nombre == 'Administrador'):
                # Superusuarios y Administradores ven todos los clientes
                return queryset
            elif user.rol and (user.rol.nombre == 'Gerente de Sucursal' or user.rol.nombre == 'Vendedor'):
                # Gerentes de Sucursal y Vendedores solo ven clientes asociados a su misma farmacia
                if user.farmacia:
                    return queryset.filter(farmacia=user.farmacia)
                else:
                    # Si no tienen farmacia asociada a su perfil, no ven clientes (esto debería ser un caso anómalo)
                    return queryset.none()
            else:
                # Otros roles autenticados que no tienen permiso explícito o farmacia asociada, no ven nada
                return queryset.none()
        # Si el usuario no está autenticado, no ve ningún cliente
        return queryset.none()
