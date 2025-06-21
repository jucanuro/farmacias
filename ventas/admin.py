# ventas/admin.py

from django.contrib import admin
from .models import Venta, DetalleVenta
from inventario.models import StockProducto, MovimientoInventario # Necesario para la lógica de stock
from django.utils import timezone # Para usar timezone.now()
from django.db import transaction # Importa transaction para asegurar la integridad de los datos

# Inline para DetalleVenta dentro de Venta
class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 1 # Número de formularios vacíos a mostrar
    raw_id_fields = ('producto', 'stock_producto') # Para buscar productos y stock eficientemente
    fields = (
        'producto', 'stock_producto', 'cantidad', 'unidad_venta',
        'precio_unitario', 'descuento_linea', 'subtotal_linea'
    )
    readonly_fields = ('subtotal_linea',) # Este campo se calcula automáticamente

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'sucursal', 'cliente', 'vendedor', 'fecha_venta',
        'tipo_comprobante', 'numero_comprobante', 'metodo_pago',
        'total_venta', 'estado_facturacion_electronica'
    )
    list_filter = (
        'sucursal', 'tipo_comprobante', 'metodo_pago',
        'estado_facturacion_electronica', 'fecha_venta'
    )
    search_fields = (
        'numero_comprobante', 'cliente__nombres', 'cliente__apellidos',
        'cliente__numero_documento', 'vendedor__username', 'sucursal__nombre'
    )
    raw_id_fields = ('sucursal', 'cliente', 'vendedor') # Para buscar eficientemente
    date_hierarchy = 'fecha_venta' # Navegar por fechas
    inlines = [DetalleVentaInline] # Muestra los detalles de la venta al editar una venta
    readonly_fields = ('total_venta', 'subtotal', 'impuestos', 'descuento_total') # Estos se calculan
    actions = ['procesar_venta'] # Acción personalizada para procesar la venta

    def save_model(self, request, obj, form, change):
        if not obj.pk: # Si es una nueva instancia
            obj.vendedor = request.user # Asigna el usuario actual como vendedor
        super().save_model(request, obj, form, change)
        # obj.calcular_totales() # Se llama en save_formset si los detalles cambian, o si se hace click en procesar

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            instance.save() # Esto activará el save() del DetalleVenta
        formset.save_m2m() # Para relaciones ManyToMany, si las hubiera
        if formset.instance:
            formset.instance.calcular_totales() # Recalcula totales de la Venta después de guardar los detalles

    # Acción personalizada para procesar la venta y actualizar el stock
    def procesar_venta(self, request, queryset):
        for venta in queryset:
            # Solo procesar ventas que no han sido procesadas o anuladas
            if venta.estado_facturacion_electronica in ['PENDIENTE', 'N/A']:
                try:
                    with transaction.atomic(): # Usa una transacción para asegurar la integridad
                        for detalle in venta.detalles.all():
                            # Asegúrate de que stock_producto no sea None y tenga la cantidad suficiente
                            if detalle.stock_producto and detalle.stock_producto.cantidad > 0:
                                detalle.actualizar_stock_por_venta(request.user)
                            else:
                                raise ValueError(f"Stock insuficiente o lote no especificado para el producto {detalle.producto.nombre} en la sucursal {venta.sucursal.nombre}.")

                        # Después de procesar el stock, actualizar el estado de la venta
                        if venta.tipo_comprobante == 'FACTURA':
                            venta.estado_facturacion_electronica = 'ENVIADO' # Cambiará a ACEPTADO/RECHAZADO por la API de FE
                        else:
                            venta.estado_facturacion_electronica = 'ACEPTADO' # O un estado final para tickets/boletas
                        venta.save()
                        self.message_user(request, f"Venta {venta.numero_comprobante or venta.id} procesada y stock actualizado correctamente.", level='success')

                except ValueError as ve:
                    self.message_user(request, f"Error al procesar la venta {venta.id}: {ve}", level='error')
                except Exception as e:
                    self.message_user(request, f"Error inesperado al procesar la venta {venta.id}: {e}", level='error')
            else:
                self.message_user(request, f"La venta {venta.numero_comprobante or venta.id} ya fue procesada o está en un estado final. Estado actual: {venta.estado_facturacion_electronica}.", level='warning')
    procesar_venta.short_description = "Procesar Venta y Actualizar Stock"


@admin.register(DetalleVenta)
class DetalleVentaAdmin(admin.ModelAdmin):
    list_display = (
        'venta', 'producto', 'cantidad', 'unidad_venta',
        'precio_unitario', 'descuento_linea', 'subtotal_linea'
    )
    list_filter = ('unidad_venta', 'producto__categoria', 'venta__sucursal')
    search_fields = ('producto__nombre', 'venta__numero_comprobante', 'venta__id')
    raw_id_fields = ('venta', 'producto', 'stock_producto')
    readonly_fields = ('subtotal_linea',)
