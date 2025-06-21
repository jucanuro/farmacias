# core/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Farmacia, Sucursal, ConfiguracionFacturacionElectronica, Rol, Usuario

# Personalizar el administrador de Usuario para incluir campos personalizados
@admin.register(Usuario)
class CustomUserAdmin(UserAdmin):
    # Añadir los campos personalizados a la interfaz de administración del usuario
    fieldsets = UserAdmin.fieldsets + (
        (('Información Adicional de Farmacia', {'fields': ('farmacia', 'sucursal', 'rol')}),)
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (('Información Adicional de Farmacia', {'fields': ('farmacia', 'sucursal', 'rol')}),)
    )
    # Mostrar los campos personalizados en la lista de usuarios
    list_display = UserAdmin.list_display + ('farmacia', 'sucursal', 'rol')
    # Permitir filtrar por los campos personalizados
    list_filter = UserAdmin.list_filter + ('farmacia', 'sucursal', 'rol')
    # Permitir buscar en los campos relacionados (usando doble guion bajo)
    search_fields = UserAdmin.search_fields + ('farmacia__nombre', 'sucursal__nombre', 'rol__nombre')
    # Para campos ForeignKey, raw_id_fields puede mejorar la experiencia de búsqueda
    raw_id_fields = ('farmacia', 'sucursal', 'rol',)


@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')
    search_fields = ('nombre',)


@admin.register(ConfiguracionFacturacionElectronica)
class ConfiguracionFacturacionElectronicaAdmin(admin.ModelAdmin):
    list_display = ('ruc_emisor', 'nombre_emisor', 'modo_produccion', 'url_base_api')
    list_filter = ('modo_produccion',)
    search_fields = ('ruc_emisor', 'nombre_emisor', 'url_base_api')


@admin.register(Farmacia)
class FarmaciaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'ruc', 'telefono', 'email', 'fecha_registro')
    search_fields = ('nombre', 'ruc', 'razon_social', 'email')
    raw_id_fields = ('configuracion_facturacion_electronica',)


@admin.register(Sucursal)
class SucursalAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'farmacia', 'codigo', 'telefono', 'administrador', 'fecha_apertura')
    list_filter = ('farmacia',) # Permite filtrar por la farmacia a la que pertenece
    search_fields = ('nombre', 'codigo', 'farmacia__nombre', 'administrador__username')
    raw_id_fields = ('administrador', 'farmacia') # Mejora la búsqueda de FK en campos con muchos registros
    date_hierarchy = 'fecha_apertura' # Navegar por fecha de apertura
