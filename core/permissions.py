# core/permissions.py
from rest_framework import permissions

class IsAdminOrManager(permissions.BasePermission):
    """
    Permiso personalizado para permitir el acceso solo a usuarios con el rol 'Administrador' o 'Gerente de Sucursal'.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # Los superusuarios siempre tienen acceso
        if request.user.is_superuser:
            return True

        # Permiso si el usuario tiene el rol de Administrador o Gerente de Sucursal
        if request.user.rol and request.user.rol.nombre in ['Administrador', 'Gerente de Sucursal']:
            return True
        return False

class IsAdminOrSelf(permissions.BasePermission):
    """
    Permiso personalizado para permitir que un usuario acceda a sus propios datos
    o si es un 'Administrador'.
    """
    def has_object_permission(self, request, view, obj):
        # Los superusuarios y administradores siempre tienen acceso
        if request.user.is_superuser or (request.user.rol and request.user.rol.nombre == 'Administrador'):
            return True

        # El propietario del objeto tiene permiso para verlo/editarlo
        # Esto asume que el objeto tiene un campo 'usuario' o 'vendedor' o 'creado_por'
        # que referencia al usuario. Se debe adaptar según el modelo.
        if hasattr(obj, 'usuario') and obj.usuario == request.user:
            return True
        if hasattr(obj, 'vendedor') and obj.vendedor == request.user:
            return True
        if hasattr(obj, 'registrado_por') and obj.registrado_por == request.user:
            return True
        if hasattr(obj, 'solicitado_por') and obj.solicitado_por == request.user:
            return True
        if hasattr(obj, 'creado_por') and obj.creado_por == request.user:
            return True

        # Para el modelo Usuario mismo, permite al usuario editar su propio perfil
        if view.basename == 'usuario' and obj == request.user:
            return True

        return False

class IsAdminOrSucursalManager(permissions.BasePermission):
    """
    Permiso personalizado para permitir el acceso a Administradores
    o a Gerentes de Sucursal que estén asociados a la sucursal del objeto.
    """
    def has_permission(self, request, view):
        # Los superusuarios siempre tienen acceso
        if request.user.is_superuser:
            return True
        
        # Permitir si el usuario es un Gerente de Sucursal (y luego has_object_permission filtrará por sucursal)
        if request.user.rol and request.user.rol.nombre == 'Gerente de Sucursal':
            return True
        
        # Un administrador general también tiene permiso
        if request.user.rol and request.user.rol.nombre == 'Administrador':
            return True
            
        return False

    def has_object_permission(self, request, view, obj):
        # Los superusuarios siempre tienen acceso
        if request.user.is_superuser:
            return True
        
        # Los administradores generales tienen acceso a todos los objetos
        if request.user.rol and request.user.rol.nombre == 'Administrador':
            return True

        # Si el usuario es un Gerente de Sucursal y el objeto está relacionado con su sucursal
        if request.user.rol and request.user.rol.nombre == 'Gerente de Sucursal':
            # Asume que el objeto tiene un campo 'sucursal'
            if hasattr(obj, 'sucursal') and obj.sucursal == request.user.sucursal:
                return True
            # Para TransferenciaStock, verifica sucursal_origen o sucursal_destino
            if view.basename == 'transferencia' and (
                (hasattr(obj, 'sucursal_origen') and obj.sucursal_origen == request.user.sucursal) or
                (hasattr(obj, 'sucursal_destino') and obj.sucursal_destino == request.user.sucursal)
            ):
                return True
        return False


class HasRolePermission(permissions.BasePermission):
    """
    Permiso genérico que verifica si el usuario tiene un rol específico.
    Se usa con `permission_classes = [HasRolePermission]` y `perm_role='NombreDelRol'`.
    """
    def has_permission(self, request, view):
        required_role = getattr(view, 'perm_role', None)
        if not required_role:
            # Si no se define un rol requerido, se asume que esta clase no es la única barrera
            # o que la vista no está correctamente configurada. Podrías optar por False aquí.
            return True # O False, dependiendo de la política predeterminada.

        if not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        return request.user.rol and request.user.rol.nombre == required_role

