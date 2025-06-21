from django.db import models

# Create your models here.
# compras/models.py

from django.db import models
from core.models import Sucursal, Usuario # Importa Sucursal y Usuario de la app 'core'
from proveedores.models import Proveedor # Importa Proveedor de la app 'proveedores'
from inventario.models import Producto, StockProducto, MovimientoInventario # Importa modelos de inventario

class CotizacionProveedor(models.Model):
    """
    Registra las cotizaciones recibidas de los proveedores para productos.
    Permite comparar precios y tomar decisiones de compra.
    """
    ESTADO_COTIZACION_CHOICES = [
        ('PENDIENTE', 'Pendiente de Revisión'),
        ('ACEPTADA', 'Aceptada (puede generar una Orden de Compra)'),
        ('RECHAZADA', 'Rechazada'),
        ('EXPIRADA', 'Expirada (fuera de fecha de validez)'),
    ]

    proveedor = models.ForeignKey(
        Proveedor, on_delete=models.PROTECT,
        verbose_name="Proveedor"
    )
    fecha_cotizacion = models.DateField(verbose_name="Fecha de Cotización")
    fecha_validez = models.DateField(blank=True, null=True, verbose_name="Fecha de Validez",
                                     help_text="Fecha hasta la cual la cotización es válida.")
    numero_cotizacion = models.CharField(max_length=100, unique=True, verbose_name="Número de Cotización",
                                         help_text="Número de referencia de la cotización del proveedor.")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Subtotal")
    impuestos = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Impuestos")
    total_cotizacion = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Total Cotización")
    estado = models.CharField(
        max_length=20, choices=ESTADO_COTIZACION_CHOICES, default='PENDIENTE',
        verbose_name="Estado de la Cotización"
    )
    observaciones = models.TextField(blank=True, verbose_name="Observaciones Adicionales")
    creado_por = models.ForeignKey(
        Usuario, on_delete=models.PROTECT,
        verbose_name="Cotización Creada Por"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")

    class Meta:
        verbose_name = "Cotización de Proveedor"
        verbose_name_plural = "Cotizaciones de Proveedores"
        ordering = ['-fecha_cotizacion', 'proveedor__nombre_comercial']

    def __str__(self):
        return f"Cotización {self.numero_cotizacion} de {self.proveedor.nombre_comercial}"

class DetalleCotizacion(models.Model):
    """Detalles de los productos y precios dentro de una cotización de proveedor."""
    cotizacion = models.ForeignKey(
        CotizacionProveedor, on_delete=models.CASCADE, related_name='detalles',
        verbose_name="Cotización Asociada"
    )
    producto = models.ForeignKey(
        Producto, on_delete=models.PROTECT,
        verbose_name="Producto Cotizado"
    )
    cantidad = models.IntegerField(verbose_name="Cantidad Cotizada")
    precio_unitario_cotizado = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio Unitario Cotizado")
    subtotal_linea = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Subtotal de Línea")

    class Meta:
        verbose_name = "Detalle de Cotización"
        verbose_name_plural = "Detalles de Cotización"
        unique_together = ('cotizacion', 'producto') # Un producto no se puede repetir en la misma cotización

    def __str__(self):
        return f"{self.cantidad} de {self.producto.nombre} en Cot. {self.cotizacion.numero_cotizacion}"

    def save(self, *args, **kwargs):
        # Calcular el subtotal de la línea antes de guardar
        self.subtotal_linea = self.cantidad * self.precio_unitario_cotizado
        super().save(*args, **kwargs)
        # Recalcular totales de la cotización principal (se puede hacer con un signal también)
        # Para evitar problemas de recursión, esto es mejor manejarlo en el `save_formset` del admin
        # o a través de un signal post_save para DetalleCotizacion.
        pass # La lógica de recálculo se manejará en el Admin o Signals

class OrdenCompra(models.Model):
    """
    Representa una orden de compra generada y enviada a un proveedor.
    Formaliza el pedido de productos.
    """
    ESTADO_OC_CHOICES = [
        ('PENDIENTE', 'Pendiente de Envío'),
        ('ENVIADA', 'Enviada al Proveedor'),
        ('RECIBIDA_PARCIAL', 'Recibida Parcialmente'),
        ('RECIBIDA_TOTAL', 'Recibida Totalmente'),
        ('CANCELADA', 'Cancelada'),
    ]

    proveedor = models.ForeignKey(
        Proveedor, on_delete=models.PROTECT,
        verbose_name="Proveedor"
    )
    sucursal_destino = models.ForeignKey(
        Sucursal, on_delete=models.PROTECT,
        verbose_name="Sucursal de Destino",
        help_text="Sucursal donde se espera recibir los productos de esta orden."
    )
    cotizacion_base = models.ForeignKey(
        CotizacionProveedor, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name="Cotización de Base",
        help_text="Cotización de la que se generó esta Orden de Compra (opcional)."
    )
    fecha_orden = models.DateField(auto_now_add=True, verbose_name="Fecha de la Orden de Compra")
    fecha_entrega_estimada = models.DateField(blank=True, null=True, verbose_name="Fecha de Entrega Estimada")
    numero_orden = models.CharField(max_length=100, unique=True, verbose_name="Número de Orden de Compra",
                                    help_text="Número único de referencia de la orden de compra.")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Subtotal")
    impuestos = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Impuestos")
    total_orden = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Total Orden")
    estado = models.CharField(
        max_length=20, choices=ESTADO_OC_CHOICES, default='PENDIENTE',
        verbose_name="Estado de la Orden"
    )
    observaciones = models.TextField(blank=True, verbose_name="Observaciones")
    creado_por = models.ForeignKey(
        Usuario, on_delete=models.PROTECT,
        verbose_name="Orden Creada Por"
    )

    class Meta:
        verbose_name = "Orden de Compra"
        verbose_name_plural = "Órdenes de Compra"
        ordering = ['-fecha_orden', 'numero_orden']

    def __str__(self):
        return f"OC {self.numero_orden} - {self.proveedor.nombre_comercial} ({self.sucursal_destino.nombre})"

    def calcular_totales(self):
        """Calcula el subtotal, impuestos y total de la orden basado en los detalles."""
        self.subtotal = sum(item.subtotal_linea for item in self.detalles.all())
        # Asumiendo un impuesto fijo del 18% para el ejemplo. Ajustar según el país.
        IMPUESTO_PORCENTAJE = models.DecimalField(max_digits=5, decimal_places=2, default=0.18)
        self.impuestos = self.subtotal * IMPUESTO_PORCENTAJE
        self.total_orden = self.subtotal + self.impuestos
        self.save()


class DetalleOrdenCompra(models.Model):
    """Detalle de los productos solicitados en una Orden de Compra."""
    orden_compra = models.ForeignKey(
        OrdenCompra, on_delete=models.CASCADE, related_name='detalles',
        verbose_name="Orden de Compra Asociada"
    )
    producto = models.ForeignKey(
        Producto, on_delete=models.PROTECT,
        verbose_name="Producto Solicitado"
    )
    cantidad_solicitada = models.IntegerField(verbose_name="Cantidad Solicitada")
    cantidad_recibida = models.IntegerField(default=0, verbose_name="Cantidad Recibida",
                                            help_text="Cantidad de este producto ya recibida para esta orden.")
    precio_unitario_oc = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio Unitario Ordenado")
    subtotal_linea = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Subtotal de Línea")

    class Meta:
        verbose_name = "Detalle de Orden de Compra"
        verbose_name_plural = "Detalles de Órdenes de Compra"
        unique_together = ('orden_compra', 'producto') # Un producto no se puede repetir en la misma OC

    def __str__(self):
        return f"{self.cantidad_solicitada} de {self.producto.nombre} en OC {self.orden_compra.numero_orden}"

    def save(self, *args, **kwargs):
        self.subtotal_linea = self.cantidad_solicitada * self.precio_unitario_oc
        super().save(*args, **kwargs)
        pass # La lógica de recálculo se manejará en el Admin o Signals

class Compra(models.Model):
    """
    Representa la recepción física de una compra de productos de un proveedor.
    Esta es la transacción que incrementa el stock real en la sucursal.
    """
    ESTADO_COMPRA_CHOICES = [
        ('PENDIENTE', 'Pendiente de Procesamiento'), # Aún no ha afectado el stock
        ('PROCESADA', 'Procesada y Stock Actualizado'), # Stock ha sido incrementado
        ('ANULADA', 'Anulada (Stock no afectado o revertido)'),
    ]

    proveedor = models.ForeignKey(
        Proveedor, on_delete=models.PROTECT,
        verbose_name="Proveedor"
    )
    sucursal_destino = models.ForeignKey(
        Sucursal, on_delete=models.PROTECT,
        verbose_name="Sucursal de Destino",
        help_text="Sucursal donde se recibirán los productos."
    )
    orden_compra_asociada = models.ForeignKey(
        OrdenCompra, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name="Orden de Compra Asociada",
        help_text="Orden de Compra a la que corresponde esta recepción (opcional)."
    )
    fecha_recepcion = models.DateField(auto_now_add=True, verbose_name="Fecha de Recepción")
    numero_factura_proveedor = models.CharField(
        max_length=100, unique=True,
        verbose_name="Número de Factura/Guía de Remisión del Proveedor",
        help_text="Número del documento fiscal emitido por el proveedor."
    )
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Subtotal")
    impuestos = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Impuestos")
    total_compra = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Total de la Compra")
    estado = models.CharField(
        max_length=20, choices=ESTADO_COMPRA_CHOICES, default='PENDIENTE',
        verbose_name="Estado de la Compra"
    )
    observaciones = models.TextField(blank=True, verbose_name="Observaciones")
    registrado_por = models.ForeignKey(
        Usuario, on_delete=models.PROTECT,
        verbose_name="Registrado Por",
        help_text="Usuario que registró la recepción de esta compra."
    )

    class Meta:
        verbose_name = "Compra (Recepción)"
        verbose_name_plural = "Compras (Recepciones)"
        ordering = ['-fecha_recepcion', 'numero_factura_proveedor']

    def __str__(self):
        return f"Compra #{self.id} - {self.proveedor.nombre_comercial} ({self.numero_factura_proveedor})"

    def calcular_totales(self):
        """Calcula el subtotal, impuestos y total de la compra basado en los detalles."""
        self.subtotal = sum(item.subtotal_linea for item in self.detalles.all())
        IMPUESTO_PORCENTAJE = models.DecimalField(max_digits=5, decimal_places=2, default=0.18)
        self.impuestos = self.subtotal * IMPUESTO_PORCENTAJE
        self.total_compra = self.subtotal + self.impuestos
        self.save()


class DetalleCompra(models.Model):
    """
    Detalle de los productos recibidos en una Compra (Recepción).
    Aquí se especifica el lote y la fecha de vencimiento para cada ítem recibido.
    """
    compra = models.ForeignKey(
        Compra, on_delete=models.CASCADE, related_name='detalles',
        verbose_name="Compra Asociada"
    )
    producto = models.ForeignKey(
        Producto, on_delete=models.PROTECT,
        verbose_name="Producto Recibido"
    )
    cantidad_recibida = models.IntegerField(verbose_name="Cantidad Recibida")
    precio_unitario_compra = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio Unitario de Compra")
    lote = models.CharField(max_length=50, verbose_name="Número de Lote")
    fecha_vencimiento = models.DateField(verbose_name="Fecha de Vencimiento del Lote")
    subtotal_linea = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Subtotal de Línea")

    class Meta:
        verbose_name = "Detalle de Compra"
        verbose_name_plural = "Detalles de Compras"
        unique_together = ('compra', 'producto', 'lote') # Un producto con el mismo lote no se puede agregar dos veces a la misma compra.

    def __str__(self):
        return f"{self.cantidad_recibida} de {self.producto.nombre} (Lote: {self.lote}) en Compra #{self.compra.id}"

    def save(self, *args, **kwargs):
        self.subtotal_linea = self.cantidad_recibida * self.precio_unitario_compra
        super().save(*args, **kwargs)
        pass # La lógica de recálculo se manejará en el Admin o Signals

    def actualizar_stock_por_compra(self, usuario_accion):
        """
        Incrementa el stock de un producto en la sucursal de destino y registra el movimiento de inventario.
        Esta función se llama cuando la compra es procesada/confirmada.
        """
        # Busca o crea la entrada de StockProducto para el lote y sucursal específicos
        stock_existente, created = StockProducto.objects.get_or_create(
            producto=self.producto,
            sucursal=self.compra.sucursal_destino,
            lote=self.lote,
            defaults={
                'fecha_vencimiento': self.fecha_vencimiento,
                'cantidad': 0 # Se inicializa en 0 si es nuevo, luego se incrementa
            }
        )

        # Si no fue creado, actualiza la fecha de vencimiento si es diferente
        if not created and stock_existente.fecha_vencimiento != self.fecha_vencimiento:
            if self.fecha_vencimiento > stock_existente.fecha_vencimiento:
                stock_existente.fecha_vencimiento = self.fecha_vencimiento

        stock_existente.cantidad += self.cantidad_recibida
        stock_existente.save()

        # Registra el movimiento en MovimientoInventario
        MovimientoInventario.objects.create(
            producto=self.producto,
            sucursal=self.compra.sucursal_destino,
            stock_afectado=stock_existente,
            tipo_movimiento='ENTRADA',
            cantidad=self.cantidad_recibida,
            usuario=usuario_accion, # El usuario que procesa la compra
            referencia_doc=f"Compra ID: {self.compra.id} / Factura: {self.compra.numero_factura_proveedor}",
            observaciones=f"Entrada por compra de {self.producto.nombre} - Lote: {self.lote}"
        )
