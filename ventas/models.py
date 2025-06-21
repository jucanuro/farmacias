# ventas/models.py

from django.db import models
from core.models import Sucursal, Usuario # Importa Sucursal y Usuario de la app 'core'
from clientes.models import Cliente # Importa Cliente de la app 'clientes'
from inventario.models import Producto, StockProducto, MovimientoInventario # Importa modelos de inventario

class Venta(models.Model):
    """
    Representa una transacción de venta completa.
    Incluye tipos de documento, métodos de pago y estado de facturación electrónica.
    """
    TIPO_COMPROBANTE_CHOICES = [
        ('TICKET', 'Ticket de Venta'),
        ('BOLETA', 'Boleta de Venta'),
        ('FACTURA', 'Factura Electrónica'),
        ('RECIBO', 'Recibo Simple'), # Para otras transacciones no fiscales
    ]

    METODO_PAGO_CHOICES = [
        ('EFECTIVO', 'Efectivo'),
        ('TARJETA_CREDITO', 'Tarjeta de Crédito'),
        ('TARJETA_DEBITO', 'Tarjeta de Débito'),
        ('YAPE', 'Yape'), # Método de pago móvil (Perú)
        ('PLIN', 'Plin'), # Método de pago móvil (Perú)
        ('CRIPTOMONEDA', 'Criptomoneda'), # Para el futuro o países específicos
        ('TRANSFERENCIA_BANCARIA', 'Transferencia Bancaria'),
        ('CREDITO_CLIENTE', 'Crédito (Cuenta Corriente Cliente)'),
        ('OTRO', 'Otro Método'),
    ]

    sucursal = models.ForeignKey(
        Sucursal, on_delete=models.PROTECT,
        verbose_name="Sucursal de Venta"
    )
    cliente = models.ForeignKey(
        Cliente, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name="Cliente Asociado",
        help_text="Cliente al que se realizó la venta (opcional si es venta genérica)."
    )
    vendedor = models.ForeignKey(
        Usuario, on_delete=models.PROTECT,
        verbose_name="Vendedor"
    )
    fecha_venta = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y Hora de Venta")
    tipo_comprobante = models.CharField(
        max_length=20, choices=TIPO_COMPROBANTE_CHOICES,
        verbose_name="Tipo de Comprobante"
    )
    numero_comprobante = models.CharField(
        max_length=50, unique=True, blank=True, null=True, # Puede generarse externamente para FE
        verbose_name="Número de Comprobante",
        help_text="Número único del documento de venta (ej. serie-correlativo)."
    )
    metodo_pago = models.CharField(
        max_length=50, choices=METODO_PAGO_CHOICES,
        verbose_name="Método de Pago Principal"
    )
    total_venta = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00,
        verbose_name="Total de la Venta"
    )
    subtotal = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00,
        verbose_name="Subtotal (Sin Impuestos)"
    )
    impuestos = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00,
        verbose_name="Impuestos (IGV/IVA)"
    )
    descuento_total = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00,
        verbose_name="Descuento Total Aplicado a la Venta"
    )
    estado_facturacion_electronica = models.CharField(
        max_length=20,
        choices=[
            ('PENDIENTE', 'Pendiente de Envío FE'),
            ('ENVIADO', 'Enviado FE'),
            ('ACEPTADO', 'Aceptado por SUNAT/AFIP/etc.'),
            ('RECHAZADO', 'Rechazado por SUNAT/AFIP/etc.'),
            ('ANULADO', 'Comprobante Anulado FE'),
            ('N/A', 'No Aplica FE'),
        ],
        default='N/A',
        verbose_name="Estado Facturación Electrónica"
    )
    uuid_comprobante_fe = models.CharField(
        max_length=100, blank=True, null=True,
        verbose_name="UUID Comprobante FE",
        help_text="Identificador único del comprobante electrónico (si aplica)."
    )

    class Meta:
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"
        ordering = ['-fecha_venta'] # Ordenar por fecha descendente

    def __str__(self):
        return f"Venta #{self.id} ({self.tipo_comprobante}) - {self.fecha_venta.strftime('%Y-%m-%d')} - {self.sucursal.nombre}"

    def calcular_totales(self):
        """Calcula el subtotal, impuestos y total de la venta basado en los detalles."""
        # Suma los subtotales de todos los detalles de venta
        self.subtotal = sum(item.subtotal_linea for item in self.detalles.all())
        # Impuesto: Asumimos un IGV/IVA del 18% para el ejemplo. Ajusta según tu país.
        IMPUESTO_PORCENTAJE = models.DecimalField(max_digits=5, decimal_places=2, default=0.18)
        self.impuestos = self.subtotal * IMPUESTO_PORCENTAJE
        # Total de la venta = Subtotal + Impuestos - Descuento total de la venta
        self.total_venta = self.subtotal + self.impuestos - self.descuento_total
        self.save()


class DetalleVenta(models.Model):
    """
    Detalle de un producto dentro de una venta.
    Permite especificar la cantidad vendida y la unidad de venta (caja, blíster, unidad).
    """
    UNIDAD_VENTA_CHOICES = [
        ('CAJA', 'Caja'),
        ('BLISTER', 'Blíster'),
        ('UNIDAD', 'Unidad (Pastilla/Cápsula)'), # Para venta por unidad suelta
        ('FRASCO', 'Frasco'),
        ('TUBO', 'Tubo'),
        ('GRAMO', 'Gramo'),
        ('MILILITRO', 'Mililitro'),
    ]

    venta = models.ForeignKey(
        Venta, on_delete=models.CASCADE, related_name='detalles',
        verbose_name="Venta Asociada"
    )
    producto = models.ForeignKey(
        Producto, on_delete=models.PROTECT,
        verbose_name="Producto Vendido"
    )
    stock_producto = models.ForeignKey(
        StockProducto, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name="Lote de Stock Afectado",
        help_text="Referencia al lote de stock específico del cual se realizó la venta (para trazabilidad)."
    ) # Esto es útil para trazabilidad del lote vendido
    cantidad = models.DecimalField(
        max_digits=10, decimal_places=2,
        verbose_name="Cantidad Vendida",
        help_text="Cantidad vendida en la 'Unidad de Venta' especificada."
    )
    unidad_venta = models.CharField(
        max_length=20, choices=UNIDAD_VENTA_CHOICES,
        verbose_name="Unidad de Venta",
        help_text="Unidad en la que se vendió el producto (ej. 'CAJA', 'BLISTER', 'UNIDAD')."
    )
    precio_unitario = models.DecimalField(
        max_digits=10, decimal_places=2,
        verbose_name="Precio Unitario (por la unidad de venta)"
    )
    subtotal_linea = models.DecimalField(
        max_digits=10, decimal_places=2,
        verbose_name="Subtotal de la Línea (sin descuento ni impuestos)"
    )
    descuento_linea = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00,
        verbose_name="Descuento por Línea"
    )

    class Meta:
        verbose_name = "Detalle de Venta"
        verbose_name_plural = "Detalles de Ventas"
        # Opcional: unique_together = ('venta', 'producto', 'stock_producto')
        # Esto evitaría añadir el mismo producto del mismo lote dos veces a la misma venta.
        # Puede ser útil si el POS no maneja agrupaciones automáticas.

    def __str__(self):
        return f"{self.cantidad} {self.unidad_venta} de {self.producto.nombre} en Venta #{self.venta.id}"

    def save(self, *args, **kwargs):
        # Calcular el subtotal de la línea antes de guardar
        self.subtotal_linea = (self.cantidad * self.precio_unitario) - self.descuento_linea
        super().save(*args, **kwargs)
        # Después de guardar el detalle, se debe asegurar que los totales de la venta padre se actualicen.
        # Esto se gestionará en el save_formset del admin o en una lógica de negocio más compleja.
        # self.venta.calcular_totales() # Descomentar si se maneja aquí directamente (puede causar recursión)


    def actualizar_stock_por_venta(self, usuario_accion):
        """
        Decrementa el stock del producto vendido en la sucursal y registra el movimiento.
        Esta lógica es crucial para la gestión de inventario.
        """
        if self.stock_producto:
            # Si se especificó un lote de stock, se decrementa de ese lote
            cantidad_base_por_unidad_venta = 1.0 # Cantidad en unidades del producto que representa 1 unidad de venta
            if self.unidad_venta == 'CAJA':
                cantidad_base_por_unidad_venta = self.producto.cantidad_por_presentacion_base
            elif self.unidad_venta == 'BLISTER':
                # Esto asume que el blíster es una subunidad de la caja,
                # necesitas definir cuántas unidades (pastillas) tiene un blíster.
                # Por ahora, un ejemplo: si un blíster tiene 10 unidades.
                # Una opción más robusta sería tener un modelo `PresentacionProducto`
                # para definir las relaciones entre Caja, Blister, Unidad.
                # Por simplicidad, asumamos que BLISTER es una cantidad fija conocida de UNIDAD
                # o una fracción de CAJA. Para este ejemplo, haremos una asunción simple.
                # Si una caja es 100 y un blister 10, entonces blister es 0.1 de caja.
                # Aquí la cantidad vendida en DETALLE_VENTA se refiere a la UNIDAD_VENTA.
                # Necesitamos convertir esa cantidad de UNIDAD_VENTA a la UNIDAD_MEDIDA del Producto.

                # Una forma es asumir que "UNIDAD" en DETALLE_VENTA es la misma que
                # la "unidad_medida" del Producto, y que CAJA/BLISTER se refieren a
                # la "presentacion_base" del Producto.
                # Si se vende 1 CAJA, se decrementa 1 de StockProducto.
                # Si se vende 1 BLISTER, necesitamos saber cuántos BLISTER hay en una CAJA.
                # Esto es una complejidad real del negocio.

                # Para simplificar y avanzar, asumiremos que StockProducto.cantidad es en
                # la `presentacion_base` del Producto. Y `DetalleVenta.cantidad` es en la
                # `unidad_venta`. Necesitamos un factor de conversión.

                # Factor de conversión a la presentación base del stock:
                factor_conversion = 1.0
                if self.unidad_venta == 'CAJA':
                    factor_conversion = 1.0 # Una caja es 1 unidad de stock_producto.cantidad
                elif self.unidad_venta == 'BLISTER':
                    # ¡IMPORTANTE! Aquí necesitas la lógica de conversión real.
                    # Por ejemplo, si en tu sistema un blíster siempre es 0.1 de una caja
                    # o tiene un número fijo de unidades de producto.
                    # POR AHORA: Si un producto `X` se vende en `caja` y tiene 100 `unidades`
                    # y un `blister` de `X` tiene 10 `unidades`.
                    # Si StockProducto guarda `cajas`, y se venden `blisters`:
                    # cantidad_a_decrementar = (self.cantidad * unidades_por_blister) / unidades_por_caja
                    # Esto requiere más información en el modelo Producto o un modelo intermedio.
                    # Para mantenerlo simple, si la unidad_venta es BLISTER, asumimos que se vende como UNIDAD de StockProducto
                    # y si la presentación_base del Producto es CAJA, esto es un error conceptual para ahora.

                    # Para evitar complejidad excesiva aquí, haremos una simplificación:
                    # Siempre se decrementará stock en la `presentacion_base` del producto,
                    # y la cantidad_vendida en `DetalleVenta` ya debería estar convertida a esa base
                    # o la venta solo se hace en `UNIDAD` si el stock es `UNIDAD`.
                    # SI el stock es en CAJAS y se vende en UNIDADES:
                    # Cantidad a decrementar del StockProducto (en su presentación base):
                    # cant_a_decrementar_base = self.cantidad / self.producto.cantidad_por_presentacion_base
                    # Por ejemplo, si vendo 5 pastillas (UNIDAD) de una CAJA de 100: 5/100 = 0.05 cajas.
                    # StockProducto.cantidad es INTEGER, por lo que tendremos que redondear o vender solo unidades enteras de CAJA.

                    # LA MEJOR MANERA ES: StockProducto.cantidad debe ser en la UNIDAD_MEDIDA más pequeña (ej. Pastillas/Unidades)
                    # Y DetalleVenta convierte la venta (ej. 1 Caja = 100 Pastillas).
                    # Para ahora, si StockProducto.cantidad es en Presentacion_Base (ej. Cajas),
                    # y DetalleVenta.cantidad es en (ej. UNIDADES o BLISTER), debemos convertir.

                    # Reajustando para un stock en la Presentacion_Base (ej. CAJAS):
                    cantidad_a_decrementar_en_base_stock = 0.0
                    if self.unidad_venta == self.producto.presentacion_base.upper():
                        # Si la unidad de venta es la misma que la presentación base (ej. vendo 1 Caja y tengo stock en Cajas)
                        cantidad_a_decrementar_en_base_stock = self.cantidad
                    elif self.unidad_venta == 'UNIDAD':
                        # Si vendo "UNIDAD" (ej. pastilla) y tengo stock en "CAJAS"
                        # Necesito cuántas unidades hay por cada "CAJA" para convertir
                        cantidad_a_decrementar_en_base_stock = self.cantidad / self.producto.cantidad_por_presentacion_base
                    elif self.unidad_venta == 'BLISTER':
                        # Esto es más complejo. Asumiremos que el blister es una cantidad fija de unidades.
                        # Por ejemplo, si un blíster tiene 10 unidades de producto
                        # Y una caja tiene 100 unidades de producto.
                        # Vendo 1 blíster, es decir 10 unidades. Afecta 0.1 de la caja.
                        # NECESITAS UN CAMPO EN PRODUCTO PARA "UNIDADES_POR_BLISTER" O SIMILAR
                        # Para este demo, asumamos 1 blíster = 10 unidades fijas para productos tipo pastillas.
                        # Y que este producto.cantidad_por_presentacion_base es para 'caja'.
                        UNIDADES_POR_BLISTER_ASUMIDO = 10 # Esto debe ser configurable por producto
                        cantidad_total_unidades_vendidas = self.cantidad * UNIDADES_POR_BLISTER_ASUMIDO
                        cantidad_a_decrementar_en_base_stock = cantidad_total_unidades_vendidas / self.producto.cantidad_por_presentacion_base
                    else:
                        # Para otras unidades de medida (gramos, mililitros), asumo que stock se maneja en esas unidades o una equivalente.
                        # Esto requeriría un factor de conversión específico.
                        cantidad_a_decrementar_en_base_stock = self.cantidad


            # El campo cantidad de StockProducto es IntegerField, por lo que no podemos tener 0.5 cajas.
            # Esto implica que solo podemos vender la presentación base completa (ej. cajas completas)
            # o que la cantidad en StockProducto debe ser en la unidad más pequeña (ej. pastillas).

            # POR LA RESTRICCIÓN DE INTEGERFIELD EN STOCKPRODUCTO.CANTIDAD,
            # NECESITAMOS ASEGURARNOS DE QUE CADA VENTA DECREMENTE CANTIDADES ENTERAS DE LA PRESENTACIÓN BASE.
            # Por ejemplo, si el stock es en cajas, solo puedes vender cajas enteras.
            # O el stock debe guardarse en "UNIDADES" (pastillas, ml, g) y la venta se convierte a esa unidad.

            # Reajuste crucial: Vamos a asumir que StockProducto.cantidad **siempre se refiere a la unidad más pequeña**
            # (ej. Pastillas, mL, Gramos), y que DetalleVenta.cantidad y unidad_venta se convierten a esa base.
            # Para esto, necesitamos refactorizar `StockProducto` y `Producto` ligeramente para que `cantidad` en `StockProducto`
            # sea siempre la unidad más granular (cantidad_por_presentacion_base * número de presentación base).
            # Para fines de este paso, ajustaré la lógica de decremento con esa asunción.

            # Cálculo de la cantidad a decrementar en la UNIDAD_MEDIDA del producto (la más granular):
            cantidad_a_decrementar_granular = 0
            if self.unidad_venta == 'UNIDAD':
                cantidad_a_decrementar_granular = self.cantidad
            elif self.unidad_venta == 'BLISTER':
                # Asumimos que 1 BLISTER = 10 UNIDADES de producto. (Esto debería ser configurable por producto)
                cantidad_a_decrementar_granular = self.cantidad * 10
            elif self.unidad_venta == 'CAJA':
                cantidad_a_decrementar_granular = self.cantidad * self.producto.cantidad_por_presentacion_base
            elif self.unidad_venta in ['GRAMO', 'MILILITRO', 'FRASCO', 'TUBO']:
                # Para estas, asumimos que la `cantidad` en DetalleVenta es ya en la unidad granular
                # o es la `presentacion_base` y su `cantidad_por_presentacion_base` es 1.
                cantidad_a_decrementar_granular = self.cantidad * self.producto.cantidad_por_presentacion_base


            if self.stock_producto.cantidad >= cantidad_a_decrementar_granular:
                self.stock_producto.cantidad -= cantidad_a_decrementar_granular
                self.stock_producto.save()

                # Registra el movimiento en MovimientoInventario
                MovimientoInventario.objects.create(
                    producto=self.producto,
                    sucursal=self.venta.sucursal,
                    stock_afectado=self.stock_producto,
                    tipo_movimiento='SALIDA',
                    cantidad=cantidad_a_decrementar_granular, # Registra la cantidad granular
                    usuario=usuario_accion,
                    referencia_doc=f"Venta ID: {self.venta.id} / Comprobante: {self.venta.numero_comprobante}",
                    observaciones=f"Salida por venta de {self.cantidad} {self.unidad_venta} de {self.producto.nombre}"
                )
            else:
                raise ValueError(f"No hay suficiente stock para {self.producto.nombre} (lote {self.stock_producto.lote}). Disponible: {self.stock_producto.cantidad}, Solicitado: {cantidad_a_decrementar_granular}.")
        else:
            raise ValueError(f"No se especificó un lote de stock para el producto {self.producto.nombre}.")

