# clientes/admin.py

from django.contrib import admin
from .models import Cliente

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = (
        'get_full_name', 'numero_documento', 'telefono', 'email',
        'farmacia', 'activo', 'fecha_registro'
    )
    list_filter = ('activo', 'tipo_documento', 'farmacia') # Filtra por estado, tipo de doc y farmacia
    search_fields = (
        'nombres', 'apellidos', 'numero_documento', 'telefono', 'email',
        'farmacia__nombre' # Permite buscar por el nombre de la farmacia relacionada
    )
    # Agrupación de campos en la vista de edición/creación
    fieldsets = (
        (None, {
            'fields': ('farmacia', 'activo')
        }),
        ('Información Personal', {
            'fields': ('nombres', 'apellidos', 'fecha_nacimiento', 'direccion', 'telefono', 'email')
        }),
        ('Identificación', {
            'fields': ('tipo_documento', 'numero_documento')
        }),
    )
    # Los campos de solo lectura no pueden ser editados directamente en el admin
    readonly_fields = ('fecha_registro',)
    # raw_id_fields es útil para campos ForeignKey si hay muchos registros
    raw_id_fields = ('farmacia',)
    date_hierarchy = 'fecha_registro' # Permite navegar por la fecha de registro
    ordering = ('-fecha_registro',) # Ordenar por los más recientes primero

