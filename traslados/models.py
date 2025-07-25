# traslados/models.py

from django.db import models, transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from core.models import Sucursal, Usuario
from inventario.models import Producto, StockProducto, MovimientoInventario

class Transferencia(models.Model):
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente de Envío'),
        ('EN_TRANSITO', 'En Tránsito'),
        ('RECIBIDO', 'Recibido'),
        ('CANCELADO', 'Cancelado'),
    ]

    sucursal_origen = models.ForeignKey(Sucursal, related_name='transferencias_enviadas', on_delete=models.PROTECT)
    sucursal_destino = models.ForeignKey(Sucursal, related_name='transferencias_recibidas', on_delete=models.PROTECT)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE')
    
    solicitado_por = models.ForeignKey(Usuario, related_name='transferencias_solicitadas', on_delete=models.PROTECT)
    enviado_por = models.ForeignKey(Usuario, related_name='transferencias_despachadas', on_delete=models.SET_NULL, null=True, blank=True)
    recibido_por = models.ForeignKey(Usuario, related_name='transferencias_aceptadas', on_delete=models.SET_NULL, null=True, blank=True)
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_envio = models.DateTimeField(null=True, blank=True)
    fecha_recepcion = models.DateTimeField(null=True, blank=True)
    
    observaciones = models.TextField(blank=True)

    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = "Transferencia"
        verbose_name_plural = "Transferencias"

    def __str__(self):
        return f"Traslado #{self.id}: {self.sucursal_origen.nombre} -> {self.sucursal_destino.nombre}"

    def clean(self):
        if self.sucursal_origen == self.sucursal_destino:
            raise ValidationError("La sucursal de origen y destino no pueden ser la misma.")

    def marcar_como_enviada(self, usuario):
        if self.estado != 'PENDIENTE':
            raise ValidationError(f"Solo se pueden enviar transferencias en estado 'PENDIENTE'.")
        
        with transaction.atomic():
            for detalle in self.detalles.all():
                stock_origen = detalle.stock_origen
                if stock_origen.cantidad < detalle.cantidad:
                    raise ValidationError(f"Stock insuficiente para {detalle.producto.nombre} (Lote: {stock_origen.lote}).")
                
                stock_origen.cantidad -= detalle.cantidad
                stock_origen.save()

                MovimientoInventario.objects.create(
                    producto=detalle.producto,
                    sucursal=self.sucursal_origen,
                    stock_afectado=stock_origen,
                    tipo_movimiento='SALIDA_TRASLADO', # Puedes añadir este tipo a tus CHOICES
                    cantidad=-detalle.cantidad,
                    usuario=usuario,
                    referencia_doc=f"Traslado ID: {self.id}"
                )
            
            self.estado = 'EN_TRANSITO'
            self.enviado_por = usuario
            self.fecha_envio = timezone.now()
            self.save()

    def marcar_como_recibida(self, usuario):
        if self.estado != 'EN_TRANSITO':
            raise ValidationError("Solo se pueden recibir transferencias 'En Tránsito'.")

        with transaction.atomic():
            for detalle in self.detalles.all():
                stock_origen = detalle.stock_origen # El lote de origen que se envió
                
                stock_destino, created = StockProducto.objects.get_or_create(
                    producto=detalle.producto,
                    sucursal=self.sucursal_destino,
                    lote=stock_origen.lote,
                    defaults={
                        'fecha_vencimiento': stock_origen.fecha_vencimiento,
                        'precio_compra': stock_origen.precio_compra,
                        'precio_venta': stock_origen.precio_venta
                    }
                )
                
                stock_destino.cantidad += detalle.cantidad
                stock_destino.save()

                MovimientoInventario.objects.create(
                    producto=detalle.producto,
                    sucursal=self.sucursal_destino,
                    stock_afectado=stock_destino,
                    tipo_movimiento='ENTRADA_TRASLADO', # Puedes añadir este tipo
                    cantidad=detalle.cantidad,
                    usuario=usuario,
                    referencia_doc=f"Traslado ID: {self.id}"
                )
            
            self.estado = 'RECIBIDO'
            self.recibido_por = usuario
            self.fecha_recepcion = timezone.now()
            self.save()


class DetalleTransferencia(models.Model):
    transferencia = models.ForeignKey(Transferencia, related_name='detalles', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    stock_origen = models.ForeignKey(
        StockProducto, 
        on_delete=models.PROTECT,
        help_text="Lote específico del cual se está enviando el producto."
    )
    cantidad = models.PositiveIntegerField()

    class Meta:
        unique_together = ('transferencia', 'stock_origen') # No puedes enviar el mismo lote dos veces en un traslado
        verbose_name = "Detalle de Transferencia"
        verbose_name_plural = "Detalles de Transferencia"

    def __str__(self):
        return f"{self.cantidad} de {self.producto.nombre} (Lote: {self.stock_origen.lote})"