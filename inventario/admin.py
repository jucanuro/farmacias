# inventario/admin.py

from django.contrib import admin

from .models import (
    CategoriaProducto,
    Laboratorio,
    PrincipioActivo,
    FormaFarmaceutica,
    UnidadPresentacion,
    Producto,
    StockProducto,
    MovimientoInventario,
    PrecioProductoSucursal,
)


@admin.register(CategoriaProducto)
class CategoriaProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')
    search_fields = ('nombre',)
    ordering = ('nombre',)


@admin.register(Laboratorio)
class LaboratorioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'telefono', 'email')
    search_fields = ('nombre', 'telefono', 'email')
    ordering = ('nombre',)


@admin.register(PrincipioActivo)
class PrincipioActivoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')
    search_fields = ('nombre',)
    ordering = ('nombre',)


@admin.register(FormaFarmaceutica)
class FormaFarmaceuticaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')
    search_fields = ('nombre',)
    ordering = ('nombre',)


@admin.register(UnidadPresentacion)
class UnidadPresentacionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'padre', 'factor_conversion')
    search_fields = ('nombre',)
    list_filter = ('padre',)
    autocomplete_fields = ('padre',)
    ordering = ('nombre',)


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = (
        'nombre',
        'sku',
        'codigo_barras',
        'categoria',
        'laboratorio',
        'unidad_compra',
        'unidad_venta',
        'precio_venta_sugerido',
        'margen_ganancia_sugerido',
        'activo',
        'aplica_receta',
        'es_controlado',
        'fecha_registro',
    )

    list_filter = (
        'activo',
        'categoria',
        'laboratorio',
        'forma_farmaceutica',
        'aplica_receta',
        'es_controlado',
        'unidad_compra',
        'unidad_venta',
        'tipo_igv',
        'precio_incluye_igv',
    )

    search_fields = (
        'nombre',
        'sku',
        'codigo_barras',
        'descripcion',
        'principio_activo__nombre',
        'laboratorio__nombre',
        'categoria__nombre',
    )

    autocomplete_fields = (
        'categoria',
        'laboratorio',
        'principio_activo',
        'forma_farmaceutica',
        'unidad_compra',
        'unidad_venta',
    )

    readonly_fields = (
        'fecha_registro',
    )

    fieldsets = (
        ('Información General', {
            'fields': (
                'nombre',
                'sku',
                'descripcion',
                'codigo_barras',
                'imagen_producto',
                'activo',
            )
        }),

        ('Información Farmacéutica', {
            'fields': (
                'principio_activo',
                'concentracion',
                'forma_farmaceutica',
                'laboratorio',
                'categoria',
            )
        }),

        ('Unidades y Presentación', {
            'fields': (
                'unidad_compra',
                'unidad_venta',
                'unidades_por_caja',
                'unidades_por_blister',
            )
        }),

        ('Precios Matriz / Sugeridos', {
            'fields': (
                'precio_venta_sugerido',
                'margen_ganancia_sugerido',
            )
        }),

        ('Impuestos', {
            'fields': (
                'tipo_igv',
                'precio_incluye_igv',
            )
        }),

        ('Control Sanitario', {
            'fields': (
                'aplica_receta',
                'es_controlado',
            )
        }),

        ('Auditoría', {
            'fields': (
                'fecha_registro',
            )
        }),
    )

    ordering = ('nombre',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'categoria',
            'laboratorio',
            'forma_farmaceutica',
            'unidad_compra',
            'unidad_venta',
        )


@admin.register(PrecioProductoSucursal)
class PrecioProductoSucursalAdmin(admin.ModelAdmin):
    list_display = (
        'producto',
        'sucursal',
        'precio_venta',
        'precio_minimo',
        'precio_mayorista',
        'usa_precio_matriz',
        'activo',
        'ultima_actualizacion',
    )

    list_filter = (
        'sucursal',
        'usa_precio_matriz',
        'activo',
        'producto__categoria',
        'producto__laboratorio',
    )

    search_fields = (
        'producto__nombre',
        'producto__sku',
        'producto__codigo_barras',
        'sucursal__nombre',
    )

    autocomplete_fields = (
        'producto',
        'sucursal',
    )

    readonly_fields = (
        'ultima_actualizacion',
    )

    ordering = (
        'sucursal__nombre',
        'producto__nombre',
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'producto',
            'sucursal',
            'producto__categoria',
            'producto__laboratorio',
        )


@admin.register(StockProducto)
class StockProductoAdmin(admin.ModelAdmin):
    list_display = (
        'producto',
        'sucursal',
        'lote',
        'cantidad_disponible',
        'cantidad_reservada',
        'cantidad_total',
        'precio_compra',
        'fecha_vencimiento',
        'ubicacion_almacen',
        'activo',
        'ultima_actualizacion',
    )

    list_filter = (
        'activo',
        'sucursal',
        'fecha_vencimiento',
        'producto__categoria',
        'producto__laboratorio',
    )

    search_fields = (
        'producto__nombre',
        'producto__sku',
        'producto__codigo_barras',
        'lote',
        'sucursal__nombre',
    )

    autocomplete_fields = (
        'producto',
        'sucursal',
    )

    readonly_fields = (
        'ultima_actualizacion',
    )

    date_hierarchy = 'fecha_vencimiento'

    ordering = (
        'producto__nombre',
        'fecha_vencimiento',
    )

    actions = [
        'marcar_revision',
    ]

    def cantidad_total(self, obj):
        return obj.cantidad_total

    cantidad_total.short_description = "Cantidad Total"

    def marcar_revision(self, request, queryset):
        self.message_user(
            request,
            f"{queryset.count()} registros enviados a revisión."
        )

    marcar_revision.short_description = "Marcar como revisión"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'producto',
            'sucursal',
            'producto__categoria',
            'producto__laboratorio',
        )


@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    list_display = (
        'producto',
        'sucursal',
        'tipo_movimiento',
        'cantidad',
        'cantidad_anterior',
        'cantidad_nueva',
        'usuario',
        'fecha_movimiento',
        'referencia_doc',
    )

    list_filter = (
        'tipo_movimiento',
        'sucursal',
        'fecha_movimiento',
        'producto__categoria',
        'producto__laboratorio',
    )

    search_fields = (
        'producto__nombre',
        'producto__sku',
        'producto__codigo_barras',
        'referencia_doc',
        'usuario__username',
        'sucursal__nombre',
    )

    autocomplete_fields = (
        'producto',
        'sucursal',
        'stock_afectado',
        'usuario',
        'sucursal_origen',
        'sucursal_destino',
    )

    readonly_fields = (
        'fecha_movimiento',
    )

    date_hierarchy = 'fecha_movimiento'

    ordering = (
        '-fecha_movimiento',
    )

    fieldsets = (
        ('Movimiento', {
            'fields': (
                'producto',
                'sucursal',
                'stock_afectado',
                'tipo_movimiento',
                'cantidad',
                'cantidad_anterior',
                'cantidad_nueva',
            )
        }),

        ('Traslado entre sucursales', {
            'fields': (
                'sucursal_origen',
                'sucursal_destino',
            )
        }),

        ('Auditoría', {
            'fields': (
                'usuario',
                'fecha_movimiento',
                'referencia_doc',
                'observaciones',
            )
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'producto',
            'sucursal',
            'stock_afectado',
            'usuario',
            'sucursal_origen',
            'sucursal_destino',
        )