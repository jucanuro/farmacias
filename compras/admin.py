# compras/admin.py

from django.contrib import admin
from .models import (
    CotizacionProveedor, DetalleCotizacion,
    OrdenCompra, DetalleOrdenCompra,
    Compra, DetalleCompra
)
from inventario.models import StockProducto, MovimientoInventario # Necesario para la lógica de stock
from django.utils import timezone # Para usar timezone.now() en acciones personalizadas
from django.db import transaction # Importa transaction para asegurar la integridad de los datos

# Inline para DetalleCotizacion
class DetalleCotizacionInline(admin.TabularInline):
    model = DetalleCotizacion
    extra = 1 # Número de formularios vacíos a mostrar
    raw_id_fields = ('producto',) # Para buscar productos eficientemente
    fields = ('producto', 'cantidad', 'precio_unitario_cotizado', 'subtotal_linea')
    readonly_fields = ('subtotal_linea',) # Este campo se calcula automáticamente

@admin.register(CotizacionProveedor)
class CotizacionProveedorAdmin(admin.ModelAdmin):
    list_display = (
        'numero_cotizacion', 'proveedor', 'fecha_cotizacion',
        'fecha_validez', 'total_cotizacion', 'estado', 'creado_por'
    )
    list_filter = ('estado', 'proveedor', 'fecha_cotizacion')
    search_fields = (
        'numero_cotizacion', 'proveedor__nombre_comercial',
        'creado_por__username', 'observaciones'
    )
    raw_id_fields = ('proveedor', 'creado_por')
    date_hierarchy = 'fecha_cotizacion'
    inlines = [DetalleCotizacionInline]
    readonly_fields = ('subtotal', 'impuestos', 'total_cotizacion', 'fecha_creacion')

    # Recalcula los totales de la cotización principal cuando los detalles cambian
    def save_formset(self, request, form, formset, change):
        super().save_formset(request, form, formset, change)
        if formset.instance:
            # Asegurarse de que la instancia de la cotización no sea None y recalcular
            formset.instance.subtotal = sum(item.subtotal_linea for item in formset.instance.detalles.all())
            IMPUESTO_PORCENTAJE = models.DecimalField(max_digits=5, decimal_places=2, default=0.18) # 18%
            formset.instance.impuestos = formset.instance.subtotal * IMPUESTO_PORCENTAJE
            formset.instance.total_cotizacion = formset.instance.subtotal + formset.instance.impuestos
            formset.instance.save()


# Inline para DetalleOrdenCompra
class DetalleOrdenCompraInline(admin.TabularInline):
    model = DetalleOrdenCompra
    extra = 1
    raw_id_fields = ('producto',)
    fields = ('producto', 'cantidad_solicitada', 'precio_unitario_oc', 'subtotal_linea', 'cantidad_recibida')
    readonly_fields = ('subtotal_linea', 'cantidad_recibida') # Cantidad recibida se actualiza en Compra

@admin.register(OrdenCompra)
class OrdenCompraAdmin(admin.ModelAdmin):
    list_display = (
        'numero_orden', 'proveedor', 'sucursal_destino', 'fecha_orden',
        'total_orden', 'estado', 'creado_por'
    )
    list_filter = ('estado', 'proveedor', 'sucursal_destino', 'fecha_orden')
    search_fields = (
        'numero_orden', 'proveedor__nombre_comercial',
        'sucursal_destino__nombre', 'creado_por__username'
    )
    raw_id_fields = ('proveedor', 'sucursal_destino', 'cotizacion_base', 'creado_por')
    date_hierarchy = 'fecha_orden'
    inlines = [DetalleOrdenCompraInline]
    readonly_fields = ('subtotal', 'impuestos', 'total_orden')

    def save_model(self, request, obj, form, change):
        # Asigna el usuario actual como quien crea la OC si es nueva
        if not obj.pk: # Si es una nueva instancia
            obj.creado_por = request.user
        super().save_model(request, obj, form, change)
        obj.calcular_totales() # Recalcula totales después de guardar la OC

    def save_formset(self, request, form, formset, change):
        super().save_formset(request, form, formset, change)
        if formset.instance:
            formset.instance.calcular_totales()


# Inline para DetalleCompra
class DetalleCompraInline(admin.TabularInline):
    model = DetalleCompra
    extra = 1
    raw_id_fields = ('producto',)
    fields = (
        'producto', 'cantidad_recibida', 'precio_unitario_compra',
        'lote', 'fecha_vencimiento', 'subtotal_linea'
    )
    readonly_fields = ('subtotal_linea',)

@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    list_display = (
        'numero_factura_proveedor', 'proveedor', 'sucursal_destino',
        'fecha_recepcion', 'total_compra', 'estado', 'registrado_por'
    )
    list_filter = ('estado', 'proveedor', 'sucursal_destino', 'fecha_recepcion')
    search_fields = (
        'numero_factura_proveedor', 'proveedor__nombre_comercial',
        'sucursal_destino__nombre', 'registrado_por__username'
    )
    raw_id_fields = ('proveedor', 'sucursal_destino', 'orden_compra_asociada', 'registrado_por')
    date_hierarchy = 'fecha_recepcion'
    inlines = [DetalleCompraInline]
    readonly_fields = ('subtotal', 'impuestos', 'total_compra')

    def save_model(self, request, obj, form, change):
        if not obj.pk: # Si es una nueva instancia
            obj.registrado_por = request.user # Asigna el usuario actual como quien registra la compra
        super().save_model(request, obj, form, change)
        obj.calcular_totales() # Recalcula totales después de guardar la compra


    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            instance.save() # Guarda el DetalleCompra, lo que llama a su propio save()
            # La lógica de actualización de stock se activará mediante la acción 'procesar_compra'
            # para dar control sobre cuándo se afecta el inventario.
        formset.save_m2m() # Para relaciones ManyToMany, si las hubiera
        if formset.instance:
            formset.instance.calcular_totales()

    # Acción personalizada para procesar la compra y actualizar el stock
    def procesar_compra(self, request, queryset):
        for compra in queryset:
            if compra.estado == 'PENDIENTE':
                try:
                    with transaction.atomic(): # Usa una transacción para asegurar la integridad
                        for detalle in compra.detalles.all():
                            detalle.actualizar_stock_por_compra(request.user) # Pasa el usuario que realiza la acción
                            # Actualizar cantidad_recibida en DetalleOrdenCompra si hay una OC asociada
                            if compra.orden_compra_asociada:
                                try:
                                    doc = DetalleOrdenCompra.objects.get(
                                        orden_compra=compra.orden_compra_asociada,
                                        producto=detalle.producto
                                    )
                                    doc.cantidad_recibida += detalle.cantidad_recibida
                                    doc.save()
                                    # La lógica para actualizar el estado de la Orden de Compra (parcial o total)
                                    # es más compleja y se puede poner en un signal o método del modelo OrdenCompra
                                    # para mantener la coherencia. Por ahora, solo actualizamos la cantidad recibida.
                                except DetalleOrdenCompra.DoesNotExist:
                                    self.message_user(request, f"Advertencia: Producto {detalle.producto.nombre} de la compra {compra.numero_factura_proveedor} no encontrado en la Orden de Compra asociada {compra.orden_compra_asociada.numero_orden}.", level='warning')
                        compra.estado = 'PROCESADA'
                        compra.save()
                        self.message_user(request, f"Compra {compra.numero_factura_proveedor} procesada y stock actualizado correctamente.", level='success')
                except Exception as e:
                    self.message_user(request, f"Error al procesar la compra {compra.numero_factura_proveedor}: {e}", level='error')
            else:
                self.message_user(request, f"La compra {compra.numero_factura_proveedor} ya fue procesada o anulada. Estado actual: {compra.estado}.", level='warning')
    procesar_compra.short_description = "Procesar y Actualizar Stock"
    actions = ['procesar_compra']
