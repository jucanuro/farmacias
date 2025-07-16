# ventas/models.py

from django.db import models
from django.conf import settings
from decimal import Decimal

from core.models import Sucursal, Usuario
from clientes.models import Cliente
from inventario.models import Producto, StockProducto, MovimientoInventario

from django.db.models import Sum, F


TIPO_COMPROBANTE_CHOICES = [
    ('TICKET', 'Ticket de Venta'),
    ('BOLETA', 'Boleta de Venta'),
    ('FACTURA', 'Factura Electrónica'),
]
METODO_PAGO_CHOICES = [
    ('EFECTIVO', 'Efectivo'),
    ('TARJETA', 'Tarjeta (Crédito/Débito)'),
    ('YAPE', 'Yape / Plin'),
    ('TRANSFERENCIA', 'Transferencia Bancaria'),
    ('OTRO', 'Otro'),
]
ESTADO_VENTA_CHOICES = [
    ('PENDIENTE', 'Pendiente'),
    ('COMPLETADA', 'Completada'),
    ('ANULADA', 'Anulada'),
]

class Venta(models.Model):
    # ... (todos tus campos de Venta no cambian) ...
    sucursal = models.ForeignKey(Sucursal, on_delete=models.PROTECT, verbose_name="Sucursal de Venta")
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Cliente Asociado")
    vendedor = models.ForeignKey(Usuario, on_delete=models.PROTECT, verbose_name="Vendedor")
    fecha_venta = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y Hora de Venta")
    tipo_comprobante = models.CharField(max_length=20, choices=TIPO_COMPROBANTE_CHOICES, verbose_name="Tipo de Comprobante")
    numero_comprobante = models.CharField(max_length=50, unique=True, blank=True, null=True, verbose_name="Número de Comprobante")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Subtotal (Sin Impuestos)")
    monto_descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Monto Total del Descuento")
    impuestos = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Impuestos (IGV/IVA)")
    total_venta = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Total de la Venta")
    metodo_pago = models.CharField(max_length=50, choices=METODO_PAGO_CHOICES, verbose_name="Método de Pago")
    monto_recibido = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Monto Recibido (Efectivo)")
    vuelto = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Vuelto Entregado")
    qr_code_data = models.TextField(blank=True, null=True, verbose_name="Datos para QR (Yape/Plin)")
    estado = models.CharField(max_length=20, choices=ESTADO_VENTA_CHOICES, default='PENDIENTE', verbose_name="Estado de la Venta")
    estado_facturacion_electronica = models.CharField(max_length=20, choices=[('PENDIENTE', 'Pendiente'), ('ENVIADO', 'Enviado'), ('ACEPTADO', 'Aceptado'), ('RECHAZADO', 'Rechazado'), ('ANULADO', 'Anulado'), ('N/A', 'No Aplica')], default='N/A', verbose_name="Estado FE")
    uuid_comprobante_fe = models.CharField(max_length=100, blank=True, null=True, verbose_name="UUID Comprobante FE")
    observaciones_fe = models.TextField(blank=True, null=True, verbose_name="Observaciones de SUNAT", help_text="Aquí se guardan los mensajes de error o reparos de SUNAT.")

    class Meta:
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"
        ordering = ['-fecha_venta']

    def __str__(self):
        return f"Venta #{self.id} ({self.tipo_comprobante}) - {self.fecha_venta.strftime('%Y-%m-%d')}"
    
    def actualizar_totales(self):
        """
        Calcula y actualiza los totales de la venta basado en sus detalles.
        """
        # Sumamos los subtotales y descuentos ya calculados en cada línea de detalle.
        agregados = self.detalles.aggregate(
            subtotal_lineas=Sum('subtotal_linea'),
            total_descuentos=Sum('monto_descuento_linea')
        )
        
        subtotal_calculado = agregados['subtotal_lineas'] or Decimal('0.0')
        descuento_calculado = agregados['total_descuentos'] or Decimal('0.0')

        self.subtotal = subtotal_calculado
        self.monto_descuento = descuento_calculado
        self.impuestos = self.subtotal * Decimal('0.18')
        self.total_venta = self.subtotal + self.impuestos
        
        self.save(update_fields=['subtotal', 'monto_descuento', 'impuestos', 'total_venta'])
    
    def save(self, *args, **kwargs):
        # No es necesario llamar a actualizar_totales() aquí.
        # La lógica se dispara desde los detalles.
        super().save(*args, **kwargs)


class DetalleVenta(models.Model):
    # ... (tus campos no cambian) ...
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles', verbose_name="Venta Asociada")
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, verbose_name="Producto Vendido")
    stock_producto = models.ForeignKey(StockProducto, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Lote de Stock Afectado")
    cantidad = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Cantidad Vendida")
    unidad_venta = models.CharField(max_length=20, verbose_name="Unidad de Venta", help_text="Unidad en la que se vendió el producto.")
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio Unitario de Venta")
    monto_descuento_linea = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Monto de Descuento")
    subtotal_linea = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Subtotal de la Línea")

    class Meta:
        verbose_name = "Detalle de Venta"
        verbose_name_plural = "Detalles de Ventas"

    def __str__(self):
        return f"{self.cantidad} de {self.producto.nombre} en Venta #{self.venta.id}"
    
    def save(self, *args, **kwargs):
        # La lógica aquí es correcta
        self.subtotal_linea = (self.cantidad * self.precio_unitario) - self.monto_descuento_linea
        super().save(*args, **kwargs)
        if self.venta:
            self.venta.actualizar_totales() 

    def delete(self, *args, **kwargs):
        venta_padre = self.venta
        super().delete(*args, **kwargs)
        # CORRECCIÓN AQUÍ: Usar el nombre de método correcto
        if venta_padre:
            venta_padre.actualizar_totales()   
        
class SesionCaja(models.Model):
    """
    Representa una sesión de caja o turno de un vendedor en una sucursal.
    """
    ESTADO_CHOICES = [
        ('ABIERTA', 'Abierta'),
        ('CERRADA', 'Cerrada'),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.PROTECT,
        verbose_name="Usuario de Caja"
    )
    sucursal = models.ForeignKey(
        'core.Sucursal', 
        on_delete=models.PROTECT,
        verbose_name="Sucursal"
    )
    monto_inicial = models.DecimalField(
        max_digits=10, decimal_places=2,
        verbose_name="Monto de Apertura"
    )
    monto_final_sistema = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        verbose_name="Monto Final (Según Sistema)"
    )
    monto_final_real = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        verbose_name="Monto Final (Contado Real)"
    )
    diferencia = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        verbose_name="Diferencia de Caja"
    )
    fecha_apertura = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha y Hora de Apertura"
    )
    fecha_cierre = models.DateTimeField(
        null=True, blank=True,
        verbose_name="Fecha y Hora de Cierre"
    )
    estado = models.CharField(
        max_length=10, 
        choices=ESTADO_CHOICES, 
        default='ABIERTA',
        verbose_name="Estado de la Sesión"
    )
    observaciones = models.TextField(blank=True, null=True, verbose_name="Observaciones de Cierre")

    class Meta:
        verbose_name = "Sesión de Caja"
        verbose_name_plural = "Sesiones de Caja"
        ordering = ['-fecha_apertura']

    def __str__(self):
        return f"Caja de {self.usuario.username} - {self.fecha_apertura.strftime('%d/%m/%Y %H:%M')}"