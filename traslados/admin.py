# traslados/admin.py

from django.contrib import admin

from .models import TrasladoStock, DetalleTrasladoStock


class DetalleTrasladoStockInline(admin.TabularInline):
    model = DetalleTrasladoStock
    extra = 1

    autocomplete_fields = (
        'producto',
        'stock_origen',
    )

    fields = (
        'producto',
        'stock_origen',
        'lote',
        'fecha_vencimiento',
        'cantidad',
        'cantidad_recibida',
        'observaciones',
    )


@admin.register(TrasladoStock)
class TrasladoStockAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'sucursal_origen',
        'sucursal_destino',
        'estado',
        'usuario_solicita',
        'usuario_envia',
        'usuario_recibe',
        'fecha_creacion',
        'fecha_envio',
        'fecha_recepcion',
    )

    list_filter = (
        'estado',
        'sucursal_origen',
        'sucursal_destino',
        'fecha_creacion',
        'fecha_envio',
        'fecha_recepcion',
    )

    search_fields = (
        'id',
        'sucursal_origen__nombre',
        'sucursal_destino__nombre',
        'usuario_solicita__username',
        'usuario_envia__username',
        'usuario_recibe__username',
        'observaciones',
    )

    autocomplete_fields = (
        'sucursal_origen',
        'sucursal_destino',
        'usuario_solicita',
        'usuario_envia',
        'usuario_recibe',
    )

    readonly_fields = (
        'fecha_creacion',
        'fecha_envio',
        'fecha_recepcion',
    )

    date_hierarchy = 'fecha_creacion'

    ordering = (
        '-fecha_creacion',
    )

    inlines = [
        DetalleTrasladoStockInline,
    ]

    fieldsets = (
        ('Sucursales', {
            'fields': (
                'sucursal_origen',
                'sucursal_destino',
            )
        }),

        ('Usuarios responsables', {
            'fields': (
                'usuario_solicita',
                'usuario_envia',
                'usuario_recibe',
            )
        }),

        ('Estado del traslado', {
            'fields': (
                'estado',
                'fecha_creacion',
                'fecha_envio',
                'fecha_recepcion',
            )
        }),

        ('Observaciones', {
            'fields': (
                'observaciones',
            )
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'sucursal_origen',
            'sucursal_destino',
            'usuario_solicita',
            'usuario_envia',
            'usuario_recibe',
        ).prefetch_related(
            'detalles__producto'
        )


@admin.register(DetalleTrasladoStock)
class DetalleTrasladoStockAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'traslado',
        'producto',
        'stock_origen',
        'lote',
        'fecha_vencimiento',
        'cantidad',
        'cantidad_recibida',
    )

    list_filter = (
        'traslado__estado',
        'fecha_vencimiento',
        'producto__categoria',
        'producto__laboratorio',
    )

    search_fields = (
        'traslado__id',
        'producto__nombre',
        'producto__sku',
        'producto__codigo_barras',
        'stock_origen__lote',
        'lote',
    )

    autocomplete_fields = (
        'traslado',
        'producto',
        'stock_origen',
    )

    ordering = (
        '-traslado__fecha_creacion',
        'producto__nombre',
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'traslado',
            'producto',
            'stock_origen',
            'producto__categoria',
            'producto__laboratorio',
        )