# inventario/admin.py

from django.contrib import admin
from .models import (
    CategoriaProducto, Laboratorio, PrincipioActivo,
    FormaFarmaceutica, Producto, StockProducto, MovimientoInventario
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

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = (
        'nombre', 'codigo_barras', 'categoria', 'laboratorio',
        'get_precio_venta_sugerido', 'aplica_receta', 'es_controlado'
    )
    list_filter = (
        'categoria', 'laboratorio', 'aplica_receta', 'es_controlado',
        'forma_farmaceutica', 'presentacion_base'
    )
    search_fields = (
        'nombre', 'codigo_barras', 'descripcion', 'principio_activo__nombre',
        'laboratorio__nombre', 'categoria__nombre'
    )
    fieldsets = (
        (None, {
            'fields': ('nombre', 'descripcion', 'codigo_barras', 'imagen_producto')
        }),
        ('Detalles del Producto Farmacéutico', {
            'fields': (
                'principio_activo', 'concentracion', 'forma_farmaceutica',
                'laboratorio', 'categoria'
            )
        }),
        ('Unidades y Precios', {
            'fields': (
                'presentacion_base', 'cantidad_por_presentacion_base',
                'unidad_medida', 'precio_compra_promedio', 'margen_ganancia_sugerido'
            ),
        }),
        ('Regulaciones Especiales', {
            'fields': ('aplica_receta', 'es_controlado'),
        }),
    )
    readonly_fields = ('fecha_registro',)
    ordering = ('nombre',)


@admin.register(StockProducto)
class StockProductoAdmin(admin.ModelAdmin):
    list_display = (
        'producto', 'sucursal', 'lote', 'fecha_vencimiento', 'cantidad', 'ubicacion_almacen', 'ultima_actualizacion'
    )
    list_filter = (
        'sucursal', 'fecha_vencimiento', 'producto__categoria', 'producto__laboratorio', 'producto__aplica_receta'
    )
    search_fields = (
        'producto__nombre', 'lote', 'sucursal__nombre', 'ubicacion_almacen',
        'producto__codigo_barras'
    )
    raw_id_fields = ('producto', 'sucursal')
    date_hierarchy = 'fecha_vencimiento'
    ordering = ('sucursal__nombre', 'producto__nombre', 'fecha_vencimiento')


@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    list_display = (
        'producto', 'sucursal', 'tipo_movimiento', 'cantidad',
        'fecha_movimiento', 'usuario', 'referencia_doc'
    )
    list_filter = (
        'tipo_movimiento', 'sucursal', 'usuario', 'fecha_movimiento',
        'producto__categoria', 'producto__laboratorio'
    )
    search_fields = (
        'producto__nombre', 'sucursal__nombre', 'usuario__username',
        'referencia_doc', 'observaciones', 'stock_afectado__lote'
    )
    raw_id_fields = ('producto', 'sucursal', 'stock_afectado', 'usuario')
    readonly_fields = ('fecha_movimiento',)
    date_hierarchy = 'fecha_movimiento'
    ordering = ('-fecha_movimiento',)
