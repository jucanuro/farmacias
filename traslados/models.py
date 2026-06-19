from django.db import models
from django.core.exceptions import ValidationError
from core.models import Sucursal, Usuario
from inventario.models import Producto, StockProducto


class TrasladoStock(models.Model):
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('ENVIADO', 'Enviado'),
        ('RECIBIDO', 'Recibido'),
        ('CANCELADO', 'Cancelado'),
        ('RECHAZADO', 'Rechazado'),
    ]

    sucursal_origen = models.ForeignKey(
        Sucursal,
        on_delete=models.PROTECT,
        related_name='traslados_salientes',
        verbose_name='Sucursal Origen'
    )

    sucursal_destino = models.ForeignKey(
        Sucursal,
        on_delete=models.PROTECT,
        related_name='traslados_entrantes',
        verbose_name='Sucursal Destino'
    )

    usuario_solicita = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name='traslados_solicitados',
        verbose_name='Usuario que Solicita'
    )

    usuario_envia = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='traslados_enviados',
        verbose_name='Usuario que Envía'
    )

    usuario_recibe = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='traslados_recibidos',
        verbose_name='Usuario que Recibe'
    )

    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='PENDIENTE',
        verbose_name='Estado'
    )

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_envio = models.DateTimeField(null=True, blank=True)
    fecha_recepcion = models.DateTimeField(null=True, blank=True)

    observaciones = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Traslado de Stock'
        verbose_name_plural = 'Traslados de Stock'
        ordering = ['-fecha_creacion']

    def clean(self):
        if self.sucursal_origen_id == self.sucursal_destino_id:
            raise ValidationError('La sucursal origen y destino no pueden ser iguales.')

    def __str__(self):
        return f'Traslado #{self.id} - {self.sucursal_origen} → {self.sucursal_destino}'
    
    

class DetalleTrasladoStock(models.Model):
    traslado = models.ForeignKey(
        TrasladoStock,
        on_delete=models.CASCADE,
        related_name='detalles',
        verbose_name='Traslado'
    )

    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        verbose_name='Producto'
    )

    stock_origen = models.ForeignKey(
        StockProducto,
        on_delete=models.PROTECT,
        related_name='detalles_traslado_origen',
        verbose_name='Stock Origen'
    )

    lote = models.CharField(
        max_length=50,
        verbose_name='Lote'
    )

    fecha_vencimiento = models.DateField(
        verbose_name='Fecha de Vencimiento'
    )

    cantidad = models.PositiveIntegerField(
        verbose_name='Cantidad a Trasladar'
    )

    cantidad_recibida = models.PositiveIntegerField(
        default=0,
        verbose_name='Cantidad Recibida'
    )

    observaciones = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Detalle de Traslado'
        verbose_name_plural = 'Detalles de Traslado'

    def clean(self):
        if self.cantidad <= 0:
            raise ValidationError('La cantidad debe ser mayor a cero.')

        if self.stock_origen and self.cantidad > self.stock_origen.cantidad_disponible:
            raise ValidationError('No hay stock suficiente para realizar el traslado.')

        if self.stock_origen and self.stock_origen.producto_id != self.producto_id:
            raise ValidationError('El stock origen no corresponde al producto seleccionado.')

    def __str__(self):
        return f'{self.producto.nombre} - {self.cantidad} unidades'