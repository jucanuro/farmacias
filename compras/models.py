from django.db import models
from django.conf import settings
from decimal import Decimal # <-- Importante añadir esta línea
from core.models import Sucursal, Usuario
from proveedores.models import Proveedor
from inventario.models import Producto, StockProducto, MovimientoInventario

class CotizacionProveedor(models.Model):
    # ... (sin cambios)
    ESTADO_COTIZACION_CHOICES = [('PENDIENTE', 'Pendiente de Revisión'), ('ACEPTADA', 'Aceptada (puede generar una Orden de Compra)'), ('RECHAZADA', 'Rechazada'), ('EXPIRADA', 'Expirada (fuera de fecha de validez)')]
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT, verbose_name="Proveedor")
    fecha_cotizacion = models.DateField(verbose_name="Fecha de Cotización")
    fecha_validez = models.DateField(blank=True, null=True, verbose_name="Fecha de Validez", help_text="Fecha hasta la cual la cotización es válida.")
    numero_cotizacion = models.CharField(max_length=100, unique=True, verbose_name="Número de Cotización", help_text="Número de referencia de la cotización del proveedor.")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Subtotal")
    impuestos = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Impuestos")
    total_cotizacion = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Total Cotización")
    estado = models.CharField(max_length=20, choices=ESTADO_COTIZACION_CHOICES, default='PENDIENTE', verbose_name="Estado de la Cotización")
    observaciones = models.TextField(blank=True, verbose_name="Observaciones Adicionales")
    creado_por = models.ForeignKey(Usuario, on_delete=models.PROTECT, verbose_name="Cotización Creada Por")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    class Meta:
        verbose_name = "Cotización de Proveedor"
        verbose_name_plural = "Cotizaciones de Proveedores"
        ordering = ['-fecha_cotizacion', 'proveedor__nombre_comercial']
    def __str__(self):
        return f"Cotización {self.numero_cotizacion} de {self.proveedor.nombre_comercial}"

class DetalleCotizacion(models.Model):
    # ... (sin cambios)
    cotizacion = models.ForeignKey(CotizacionProveedor, on_delete=models.CASCADE, related_name='detalles', verbose_name="Cotización Asociada")
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, verbose_name="Producto Cotizado")
    cantidad = models.IntegerField(verbose_name="Cantidad Cotizada")
    precio_unitario_cotizado = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio Unitario Cotizado")
    subtotal_linea = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Subtotal de Línea")
    class Meta:
        verbose_name = "Detalle de Cotización"
        verbose_name_plural = "Detalles de Cotización"
        unique_together = ('cotizacion', 'producto')
    def __str__(self):
        return f"{self.cantidad} de {self.producto.nombre} en Cot. {self.cotizacion.numero_cotizacion}"
    def save(self, *args, **kwargs):
        self.subtotal_linea = self.cantidad * self.precio_unitario_cotizado
        super().save(*args, **kwargs)

class OrdenCompra(models.Model):
    # ... (código existente)
    ESTADO_OC_CHOICES = [('PENDIENTE', 'Pendiente de Envío'), ('ENVIADA', 'Enviada al Proveedor'), ('RECIBIDA_PARCIAL', 'Recibida Parcialmente'), ('RECIBIDA_TOTAL', 'Recibida Totalmente'), ('CANCELADA', 'Cancelada')]
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT, verbose_name="Proveedor")
    sucursal_destino = models.ForeignKey(Sucursal, on_delete=models.PROTECT, verbose_name="Sucursal de Destino", help_text="Sucursal donde se espera recibir los productos de esta orden.")
    cotizacion_base = models.ForeignKey(CotizacionProveedor, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Cotización de Base", help_text="Cotización de la que se generó esta Orden de Compra (opcional).")
    fecha_orden = models.DateField(auto_now_add=True, verbose_name="Fecha de la Orden de Compra")
    fecha_entrega_estimada = models.DateField(blank=True, null=True, verbose_name="Fecha de Entrega Estimada")
    numero_orden = models.CharField(max_length=100, unique=True, verbose_name="Número de Orden de Compra", help_text="Número único de referencia de la orden de compra.")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Subtotal")
    impuestos = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Impuestos")
    total_orden = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Total Orden")
    estado = models.CharField(max_length=20, choices=ESTADO_OC_CHOICES, default='PENDIENTE', verbose_name="Estado de la Orden")
    observaciones = models.TextField(blank=True, verbose_name="Observaciones")
    creado_por = models.ForeignKey(Usuario, on_delete=models.PROTECT, verbose_name="Orden Creada Por")
    class Meta:
        verbose_name = "Orden de Compra"
        verbose_name_plural = "Órdenes de Compra"
        ordering = ['-fecha_orden', 'numero_orden']
    def __str__(self):
        return f"OC {self.numero_orden} - {self.proveedor.nombre_comercial} ({self.sucursal_destino.nombre})"

    def calcular_totales(self):
        self.subtotal = sum(item.subtotal_linea for item in self.detalles.all())
        # --- CORRECCIÓN AQUÍ ---
        IMPUESTO_PORCENTAJE = Decimal('0.18')
        self.impuestos = self.subtotal * IMPUESTO_PORCENTAJE
        self.total_orden = self.subtotal + self.impuestos
        self.save()

class DetalleOrdenCompra(models.Model):
    # ... (sin cambios)
    orden_compra = models.ForeignKey(OrdenCompra, on_delete=models.CASCADE, related_name='detalles', verbose_name="Orden de Compra Asociada")
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, verbose_name="Producto Solicitado")
    cantidad_solicitada = models.IntegerField(verbose_name="Cantidad Solicitada")
    cantidad_recibida = models.IntegerField(default=0, verbose_name="Cantidad Recibida", help_text="Cantidad de este producto ya recibida para esta orden.")
    precio_unitario_oc = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio Unitario Ordenado")
    subtotal_linea = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Subtotal de Línea")
    class Meta:
        verbose_name = "Detalle de Orden de Compra"
        verbose_name_plural = "Detalles de Órdenes de Compra"
        unique_together = ('orden_compra', 'producto')
    def __str__(self):
        return f"{self.cantidad_solicitada} de {self.producto.nombre} en OC {self.orden_compra.numero_orden}"
    def save(self, *args, **kwargs):
        self.subtotal_linea = self.cantidad_solicitada * self.precio_unitario_oc
        super().save(*args, **kwargs)

class Compra(models.Model):
    # ... (código existente)
    ESTADO_COMPRA_CHOICES = [('PENDIENTE', 'Pendiente de Procesamiento'), ('PROCESADA', 'Procesada y Stock Actualizado'), ('ANULADA', 'Anulada (Stock no afectado o revertido)')]
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT, verbose_name="Proveedor")
    sucursal_destino = models.ForeignKey(Sucursal, on_delete=models.PROTECT, verbose_name="Sucursal de Destino", help_text="Sucursal donde se recibirán los productos.")
    orden_compra_asociada = models.ForeignKey(OrdenCompra, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Orden de Compra Asociada", help_text="Orden de Compra a la que corresponde esta recepción (opcional).")
    fecha_recepcion = models.DateField(auto_now_add=True, verbose_name="Fecha de Recepción")
    numero_factura_proveedor = models.CharField(max_length=100, unique=True, verbose_name="Número de Factura/Guía de Remisión del Proveedor", help_text="Número del documento fiscal emitido por el proveedor.")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Subtotal")
    impuestos = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Impuestos")
    total_compra = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Total de la Compra")
    estado = models.CharField(max_length=20, choices=ESTADO_COMPRA_CHOICES, default='PENDIENTE', verbose_name="Estado de la Compra")
    observaciones = models.TextField(blank=True, verbose_name="Observaciones")
    registrado_por = models.ForeignKey(Usuario, on_delete=models.PROTECT, verbose_name="Registrado Por", help_text="Usuario que registró la recepción de esta compra.")
    class Meta:
        verbose_name = "Compra (Recepción)"
        verbose_name_plural = "Compras (Recepciones)"
        ordering = ['-fecha_recepcion', 'numero_factura_proveedor']
    def __str__(self):
        return f"Compra #{self.id} - {self.proveedor.nombre_comercial} ({self.numero_factura_proveedor})"

    def calcular_totales(self):
        self.subtotal = sum(item.subtotal_linea for item in self.detalles.all())
        # --- CORRECCIÓN AQUÍ ---
        IMPUESTO_PORCENTAJE = Decimal('0.18')
        self.impuestos = self.subtotal * IMPUESTO_PORCENTAJE
        self.total_compra = self.subtotal + self.impuestos
        self.save()

class DetalleCompra(models.Model):
    # ... (código existente)
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE, related_name='detalles', verbose_name="Compra Asociada")
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, verbose_name="Producto Recibido")
    cantidad_recibida = models.IntegerField(verbose_name="Cantidad Recibida")
    precio_unitario_compra = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio Unitario de Compra")
    lote = models.CharField(max_length=50, verbose_name="Número de Lote")
    fecha_vencimiento = models.DateField(verbose_name="Fecha de Vencimiento del Lote")
    subtotal_linea = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Subtotal de Línea")
    class Meta:
        verbose_name = "Detalle de Compra"
        verbose_name_plural = "Detalles de Compras"
        unique_together = ('compra', 'producto', 'lote')
    def __str__(self):
        return f"{self.cantidad_recibida} de {self.producto.nombre} (Lote: {self.lote}) en Compra #{self.compra.id}"
    def save(self, *args, **kwargs):
        self.subtotal_linea = self.cantidad_recibida * self.precio_unitario_compra
        super().save(*args, **kwargs)
    def actualizar_stock_por_compra(self, usuario_accion):
        stock_existente, created = StockProducto.objects.get_or_create(
            producto=self.producto, sucursal=self.compra.sucursal_destino, lote=self.lote,
            defaults={'fecha_vencimiento': self.fecha_vencimiento, 'cantidad': 0}
        )
        if not created and self.fecha_vencimiento and stock_existente.fecha_vencimiento != self.fecha_vencimiento:
            if self.fecha_vencimiento > stock_existente.fecha_vencimiento:
                stock_existente.fecha_vencimiento = self.fecha_vencimiento
        stock_existente.cantidad += self.cantidad_recibida
        stock_existente.save()
        MovimientoInventario.objects.create(
            producto=self.producto, sucursal=self.compra.sucursal_destino,
            stock_afectado=stock_existente, tipo_movimiento='ENTRADA',
            cantidad=self.cantidad_recibida, usuario=usuario_accion,
            referencia_doc=f"Compra ID: {self.compra.id} / Factura: {self.compra.numero_factura_proveedor}",
            observaciones=f"Entrada por compra de {self.producto.nombre} - Lote: {self.lote}"
        )