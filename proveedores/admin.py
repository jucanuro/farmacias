# proveedores/admin.py

from django.contrib import admin
from .models import Proveedor

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = (
        'nombre_comercial', 'razon_social', 'numero_documento',
        'telefono', 'email', 'activo', 'fecha_registro'
    )
    list_filter = ('activo', 'tipo_documento',) # Filtra por estado y tipo de documento
    search_fields = (
        'nombre_comercial', 'razon_social', 'numero_documento',
        'persona_contacto', 'email', 'telefono'
    )
    # Agrupación de campos para la vista de edición/creación
    fieldsets = (
        (None, {
            'fields': ('nombre_comercial', 'razon_social', 'activo')
        }),
        ('Información de Contacto y Fiscal', {
            'fields': (
                'tipo_documento', 'numero_documento', 'direccion',
                'telefono', 'email', 'sitio_web'
            )
        }),
        ('Contacto Adicional y Condiciones', {
            'fields': (
                'persona_contacto', 'telefono_contacto', 'condiciones_pago'
            )
        }),
    )
    readonly_fields = ('fecha_registro',) # Este campo se autogenera
    ordering = ('-fecha_registro',) # Ordenar por los más recientes primero

