# ventas/admin.py

from django.contrib import admin
from .models import Venta, DetalleVenta

# Inline para DetalleVenta dentro de Venta
class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 1
    raw_id_fields = ('producto', 'stock_producto')
    # --- CORREGIDO: Usamos el nombre de campo actualizado 'monto_descuento_linea' ---
    fields = (
        'producto', 'stock_producto', 'cantidad', 'unidad_venta',
        'precio_unitario', 'monto_descuento_linea', 'subtotal_linea'
    )
    readonly_fields = ('subtotal_linea',)

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'sucursal', 'cliente', 'vendedor', 'fecha_venta',
        'tipo_comprobante', 'numero_comprobante', 'metodo_pago',
        'total_venta', 'estado', 'estado_facturacion_electronica'
    )
    list_filter = (
        'estado', 'sucursal', 'tipo_comprobante', 'metodo_pago',
        'estado_facturacion_electronica', 'fecha_venta'
    )
    search_fields = (
        'numero_comprobante', 'cliente__nombres', 'cliente__apellidos',
        'cliente__numero_documento', 'vendedor__username', 'sucursal__nombre'
    )
    raw_id_fields = ('sucursal', 'cliente', 'vendedor')
    date_hierarchy = 'fecha_venta'
    inlines = [DetalleVentaInline]
    
    # --- CORREGIDO: Usamos 'monto_descuento' en lugar de 'descuento_total' ---
    readonly_fields = ('total_venta', 'subtotal', 'impuestos', 'monto_descuento', 'vuelto')
    
    # La acción 'procesar_venta' no necesita cambios, ya que no usa los campos renombrados.
    # La hemos quitado por ahora para simplificar, ya que esta lógica se manejará en el ViewSet.
    # actions = ['procesar_venta'] 

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.vendedor = request.user
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        # Esta función guarda los detalles y luego llama a calcular_totales en la Venta
        instances = formset.save()
        if instances:
             # Llama a calcular_totales en la instancia de la venta asociada.
             # Se asume que todos los detalles pertenecen a la misma venta.
            instances[0].venta.calcular_totales()

@admin.register(DetalleVenta)
class DetalleVentaAdmin(admin.ModelAdmin):
    # --- CORREGIDO: Usamos 'monto_descuento_linea' en lugar de 'descuento_linea' ---
    list_display = (
        'venta', 'producto', 'cantidad', 'unidad_venta',
        'precio_unitario', 'monto_descuento_linea', 'subtotal_linea'
    )
    # El filtro por 'unidad_venta' ahora funcionará porque el campo ya existe en el modelo.
    list_filter = ('unidad_venta', 'producto__categoria', 'venta__sucursal')
    search_fields = ('producto__nombre', 'venta__numero_comprobante', 'venta__id')
    raw_id_fields = ('venta', 'producto', 'stock_producto')
    readonly_fields = ('subtotal_linea',)