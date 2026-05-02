# traslados/admin.py

from django.contrib import admin
from .models import Transferencia, DetalleTransferencia

class DetalleTransferenciaInline(admin.TabularInline):
    """Permite ver y editar los detalles de la transferencia en la misma página."""
    model = DetalleTransferencia
    extra = 1 
    raw_id_fields = ('stock_origen',) 
    autocomplete_fields = ('producto',) 

@admin.register(Transferencia)
class TransferenciaAdmin(admin.ModelAdmin):
    """Configuración del panel de administrador para el modelo Transferencia."""
    list_display = (
        'id', 'sucursal_origen', 'sucursal_destino', 
        'estado', 'solicitado_por', 'fecha_creacion'
    )
    list_filter = ('estado', 'sucursal_origen', 'sucursal_destino')
    search_fields = ('id', 'observaciones')
    inlines = [DetalleTransferenciaInline] 
    readonly_fields = ('fecha_creacion', 'fecha_envio', 'fecha_recepcion')
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('detalles__producto')

@admin.register(DetalleTransferencia)
class DetalleTransferenciaAdmin(admin.ModelAdmin):
    """Configuración para el modelo DetalleTransferencia (opcional)."""
    list_display = ('id', 'transferencia', 'producto', 'stock_origen', 'cantidad')
    list_filter = ('producto',)
    search_fields = ('transferencia__id', 'producto__nombre', 'stock_origen__lote')