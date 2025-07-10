# ventas/models.py

from django.db import models
from decimal import Decimal
from core.models import Sucursal, Usuario
from clientes.models import Cliente
from inventario.models import Producto, StockProducto, MovimientoInventario

class Venta(models.Model):
    """
    Representa una transacción de venta completa.
    Incluye tipos de documento, métodos de pago y estado de facturación electrónica.
    """
    TIPO_COMPROBANTE_CHOICES = [
        ('TICKET', 'Ticket de Venta'),
        ('BOLETA', 'Boleta de Venta'),
        ('FACTURA', 'Factura Electrónica'),
    ]

    METODO_PAGO_CHOICES = [
        ('EFECTIVO', 'Efectivo'),
        ('TARJETA', 'Tarjeta (Crédito/Débito)'), # <-- SIMPLIFICADO
        ('YAPE', 'Yape / Plin'), # <-- AGRUPADO
        ('TRANSFERENCIA', 'Transferencia Bancaria'), # <-- SIMPLIFICADO
        ('OTRO', 'Otro'),
    ]

    ESTADO_VENTA_CHOICES = [
        ('PENDIENTE', 'Pendiente'), # Carrito activo en el POS
        ('COMPLETADA', 'Completada'), # Venta finalizada y pagada
        ('ANULADA', 'Anulada'), # Venta cancelada
    ]

    # --- Campos existentes (con pequeños ajustes) ---
    sucursal = models.ForeignKey(Sucursal, on_delete=models.PROTECT, verbose_name="Sucursal de Venta")
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Cliente Asociado")
    vendedor = models.ForeignKey(Usuario, on_delete=models.PROTECT, verbose_name="Vendedor")
    fecha_venta = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y Hora de Venta")
    tipo_comprobante = models.CharField(max_length=20, choices=TIPO_COMPROBANTE_CHOICES, verbose_name="Tipo de Comprobante")
    numero_comprobante = models.CharField(max_length=50, unique=True, blank=True, null=True, verbose_name="Número de Comprobante")
    
    # --- Campos de totales y descuentos ---
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Subtotal (Sin Impuestos)")
    monto_descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Monto Total del Descuento") # <-- RENOMBRADO
    impuestos = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Impuestos (IGV/IVA)")
    total_venta = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Total de la Venta")
    
    # --- Campos para el Proceso de Pago ---
    metodo_pago = models.CharField(max_length=50, choices=METODO_PAGO_CHOICES, verbose_name="Método de Pago") # <-- CAMPO EXISTENTE
    monto_recibido = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Monto Recibido (Efectivo)") # <-- AÑADIDO
    vuelto = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Vuelto Entregado") # <-- AÑADIDO
    qr_code_data = models.TextField(blank=True, null=True, verbose_name="Datos para QR (Yape/Plin)") # <-- AÑADIDO
    
    # --- Campos de Estado y Facturación Electrónica ---
    estado = models.CharField(max_length=20, choices=ESTADO_VENTA_CHOICES, default='PENDIENTE', verbose_name="Estado de la Venta") # <-- AÑADIDO
    estado_facturacion_electronica = models.CharField(max_length=20, choices=[('PENDIENTE', 'Pendiente'), ('ENVIADO', 'Enviado'), ('ACEPTADO', 'Aceptado'), ('RECHAZADO', 'Rechazado'), ('ANULADO', 'Anulado'), ('N/A', 'No Aplica')], default='N/A', verbose_name="Estado FE")
    uuid_comprobante_fe = models.CharField(max_length=100, blank=True, null=True, verbose_name="UUID Comprobante FE")
    observaciones_fe = models.TextField(
        blank=True, null=True,
        verbose_name="Observaciones de SUNAT",
        help_text="Aquí se guardan los mensajes de error o reparos de SUNAT."
    )

    class Meta:
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"
        ordering = ['-fecha_venta']

    def __str__(self):
        return f"Venta #{self.id} ({self.tipo_comprobante}) - {self.fecha_venta.strftime('%Y-%m-%d')}"

    def calcular_totales(self):
        """
        Calcula y actualiza los totales de la venta basado en sus detalles.
        Este método debe ser llamado cada vez que se añade, modifica o elimina un detalle.
        """
        detalles = self.detalles.all()
        # Suma los subtotales y descuentos de cada línea de producto
        subtotal_bruto = sum(item.precio_unitario * item.cantidad for item in detalles)
        descuento_por_items = sum(item.monto_descuento_linea for item in detalles)

        self.subtotal = subtotal_bruto - descuento_por_items
        
        # Asumimos un IGV del 18%. Esto debería ser configurable en un futuro.
        self.impuestos = self.subtotal * Decimal('0.18')
        self.total_venta = self.subtotal + self.impuestos
        self.monto_descuento = descuento_por_items # Se podría añadir un descuento global extra aquí si se quisiera
        
        self.save()


class DetalleVenta(models.Model):
    """
    Detalle de un producto dentro de una venta.
    """
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles', verbose_name="Venta Asociada")
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, verbose_name="Producto Vendido")
    stock_producto = models.ForeignKey(StockProducto, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Lote de Stock Afectado")
    cantidad = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Cantidad Vendida")
    unidad_venta = models.CharField(
        max_length=20, 
        verbose_name="Unidad de Venta",
        help_text="Unidad en la que se vendió el producto."
    )
    
    # El precio al que se vendió, puede ser diferente al precio de lista del producto
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio Unitario de Venta")
    
    # --- Campos de Descuento por Línea ---
    monto_descuento_linea = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Monto de Descuento") # <-- RENOMBRADO
    
    # Campo calculado, no necesita guardarse en la BD si se calcula en el momento.
    # Pero lo guardamos para facilitar los reportes.
    subtotal_linea = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Subtotal de la Línea")

    class Meta:
        verbose_name = "Detalle de Venta"
        verbose_name_plural = "Detalles de Ventas"

    def __str__(self):
        return f"{self.cantidad} de {self.producto.nombre} en Venta #{self.venta.id}"

    def save(self, *args, **kwargs):
        # Calcular el subtotal de la línea antes de guardar
        self.subtotal_linea = (self.cantidad * self.precio_unitario) - self.monto_descuento_linea
        super().save(*args, **kwargs)
        # Después de guardar, le decimos a la venta padre que recalcule sus totales
        self.venta.calcular_totales()

    def delete(self, *args, **kwargs):
        venta_padre = self.venta
        super().delete(*args, **kwargs)
        # Después de borrar, también recalculamos
        venta_padre.calcular_totales()