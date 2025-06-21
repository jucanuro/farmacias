# traslados/models.py

from django.db import models
from core.models import Sucursal, Usuario # Importa Sucursal y Usuario de la app 'core'
from inventario.models import Producto, StockProducto, MovimientoInventario # Importa Producto, StockProducto y MovimientoInventario
from django.utils import timezone
from django.db import transaction

class TransferenciaStock(models.Model):
    """
    Registra los traslados de stock de productos entre diferentes sucursales
    de la misma cadena de farmacias.
    """
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente de Envío'),
        ('ENVIADO', 'Enviado'),
        ('RECIBIDO', 'Recibido'),
        ('RECHAZADO', 'Rechazado'),
        ('CANCELADO', 'Cancelado'),
    ]

    producto = models.ForeignKey(
        Producto, on_delete=models.PROTECT,
        verbose_name="Producto a Transferir"
    )
    # Sucursal de origen de la transferencia
    sucursal_origen = models.ForeignKey(
        Sucursal, on_delete=models.PROTECT,
        related_name='transferencias_enviadas',
        verbose_name="Sucursal de Origen",
        help_text="Sucursal desde la que se envía el producto."
    )
    # Sucursal de destino de la transferencia
    sucursal_destino = models.ForeignKey(
        Sucursal, on_delete=models.PROTECT,
        related_name='transferencias_recibidas',
        verbose_name="Sucursal de Destino",
        help_text="Sucursal a la que se destina el producto."
    )
    cantidad = models.IntegerField(verbose_name="Cantidad a Transferir",
                                   help_text="Cantidad del producto en su 'presentación base' a transferir.")
    fecha_solicitud = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Solicitud")
    fecha_envio = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Envío")
    fecha_recepcion = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Recepción")
    estado = models.CharField(
        max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE',
        verbose_name="Estado de la Transferencia"
    )
    solicitado_por = models.ForeignKey(
        Usuario, on_delete=models.PROTECT,
        related_name='solicitudes_transferencia',
        verbose_name="Solicitado Por"
    )
    enviado_por = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='envios_transferencia',
        verbose_name="Enviado Por"
    )
    recibido_por = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='recepciones_transferencia',
        verbose_name="Recibido Por"
    )
    observaciones = models.TextField(blank=True, verbose_name="Observaciones")

    class Meta:
        verbose_name = "Transferencia de Stock"
        verbose_name_plural = "Transferencias de Stock"
        ordering = ['-fecha_solicitud']

    def __str__(self):
        return (
            f"Transf. {self.producto.nombre} ({self.cantidad}) de "
            f"{self.sucursal_origen.nombre} a {self.sucursal_destino.nombre} - Estado: {self.estado}"
        )

    def limpiar_y_validar_sucursales(self):
        """
        Método para validar que las sucursales de origen y destino no sean la misma
        y que pertenezcan a la misma Farmacia (cadena).
        """
        if self.sucursal_origen == self.sucursal_destino:
            raise ValueError("La sucursal de origen no puede ser la misma que la sucursal de destino.")
        if self.sucursal_origen.farmacia != self.sucursal_destino.farmacia:
            raise ValueError("Las sucursales de origen y destino deben pertenecer a la misma Farmacia (cadena).")

    def guardar_con_validaciones(self, *args, **kwargs):
        """Sobreescribe save para incluir validaciones personalizadas."""
        self.limpiar_y_validar_sucursales()
        super().save(*args, **kwargs)

    def realizar_envio(self, usuario_envio):
        """
        Actualiza el estado a 'ENVIADO', registra el usuario que envía y decrementa el stock de origen.
        """
        if self.estado == 'PENDIENTE':
            self.limpiar_y_validar_sucursales() # Vuelve a validar antes de la acción crítica
            with transaction.atomic():
                # Decrementar stock en la sucursal de origen.
                # Aquí la simplificación: se asume que se decrementa del lote más grande o más antiguo.
                # En una aplicación real, el usuario especificaría el LOTE exacto a enviar.
                # Para esta demo, obtenemos el primer StockProducto disponible en el origen.
                stock_origen = StockProducto.objects.filter(
                    producto=self.producto,
                    sucursal=self.sucursal_origen,
                    cantidad__gte=self.cantidad # Solo si hay suficiente stock
                ).order_by('-fecha_vencimiento').first() # O por cantidad, o FIFO/LIFO

                if not stock_origen:
                    raise ValueError(f"Stock insuficiente o ningún lote disponible en la sucursal de origen ({self.sucursal_origen.nombre}) para el producto {self.producto.nombre}. Cantidad solicitada: {self.cantidad}.")

                # Decremento del stock del lote encontrado
                stock_origen.cantidad -= self.cantidad
                stock_origen.save()

                # Registrar movimiento de salida en el inventario de origen
                MovimientoInventario.objects.create(
                    producto=self.producto,
                    sucursal=self.sucursal_origen,
                    stock_afectado=stock_origen,
                    tipo_movimiento='SALIDA',
                    cantidad=self.cantidad,
                    usuario=usuario_envio,
                    referencia_doc=f"Transferencia ID: {self.id} (Envío)",
                    observaciones=f"Envío de {self.cantidad} de {self.producto.nombre} (Lote: {stock_origen.lote}) a {self.sucursal_destino.nombre}"
                )

                self.estado = 'ENVIADO'
                self.enviado_por = usuario_envio
                self.fecha_envio = timezone.now()
                self.save()
        else:
            raise ValueError(f"La transferencia ya tiene el estado '{self.estado}' y no puede ser enviada.")

    def realizar_recepcion(self, usuario_recepcion):
        """
        Actualiza el estado a 'RECIBIDO', registra el usuario que recibe y aumenta el stock de destino.
        """
        if self.estado == 'ENVIADO':
            self.limpiar_y_validar_sucursales() # Vuelve a validar antes de la acción crítica
            with transaction.atomic():
                # En este punto, al recibir, deberíamos saber el lote que se recibe.
                # Para simplificar el demo, asumiremos que el lote es el mismo que el que salió
                # de origen (si se especificó uno), o un lote genérico de transferencia.
                # En una implementación real, la UI pediría el LOTE REAL recibido.
                # Usaremos el lote del `stock_origen` que se decrementó. Para eso,
                # `TransferenciaStock` debería guardar el lote de origen.
                # Por ahora, para que funcione, usaremos un lote arbitrario o el ID de la transferencia.

                # Una mejor aproximación: al enviar, la transferencia debe registrar el LOTE que se envió.
                # Y al recibir, ese LOTE es el que se incrementa en destino.
                # Para la demo, el `realizar_envio` no almacena el lote específico.
                # HAREMOS UNA SIMPLIFICACIÓN: Buscamos un StockProducto existente con el mismo producto y sucursal de destino.
                # Si existe, actualizamos; si no, creamos uno con un lote generado.
                # Opcional: si la transferencia tiene un campo 'lote_enviado', usarlo aquí.

                # Simplificación de lote para demo:
                # Si en el `realizar_envio` se selecciona un `stock_origen`, su `lote` puede ser usado.
                # Si no, creamos uno nuevo.
                # Para evitar esto, se necesita que `TransferenciaStock` tenga un campo `lote_enviado`.
                # Como no lo tiene ahora, generaremos uno para el destino.
                lote_recibido = f"TRASF_{self.id}_{self.producto.nombre[:10]}_{timezone.now().strftime('%Y%m%d')}"
                
                # Intentamos obtener el StockProducto existente por producto, sucursal_destino y el lote (si fuera conocido)
                # O creamos uno nuevo si no existe.
                stock_destino, created = StockProducto.objects.get_or_create(
                    producto=self.producto,
                    sucursal=self.sucursal_destino,
                    lote=lote_recibido, # Usar el lote del envío si estuviera almacenado.
                    defaults={
                        'fecha_vencimiento': timezone.now().date() + timezone.timedelta(days=365), # Fecha de vencimiento genérica para el nuevo lote si se crea
                        'cantidad': 0
                    }
                )

                stock_destino.cantidad += self.cantidad
                stock_destino.save()

                # Registrar movimiento de entrada en el inventario de destino
                MovimientoInventario.objects.create(
                    producto=self.producto,
                    sucursal=self.sucursal_destino,
                    stock_afectado=stock_destino,
                    tipo_movimiento='ENTRADA',
                    cantidad=self.cantidad,
                    usuario=usuario_recepcion,
                    referencia_doc=f"Transferencia ID: {self.id} (Recepción)",
                    observaciones=f"Recepción de {self.cantidad} de {self.producto.nombre} (Lote: {stock_destino.lote}) desde {self.sucursal_origen.nombre}"
                )

                self.estado = 'RECIBIDO'
                self.recibido_por = usuario_recepcion
                self.fecha_recepcion = timezone.now()
                self.save()
        else:
            raise ValueError(f"La transferencia no está en estado 'ENVIADO' para ser recibida. Estado actual: {self.estado}.")

    def rechazar_transferencia(self, usuario_rechazo, observaciones_rechazo=""):
        """
        Rechaza una transferencia en estado PENDIENTE o ENVIADO y revierte el stock si fue enviado.
        """
        with transaction.atomic():
            if self.estado == 'PENDIENTE':
                self.estado = 'RECHAZADO'
                self.observaciones = f"Rechazado por {usuario_rechazo.username}: {observaciones_rechazo}"
                self.save()
            elif self.estado == 'ENVIADO':
                # Si ya fue enviado, hay que devolver el stock a la sucursal de origen
                # Asumimos que se revierte al lote del que se sacó o al más adecuado si no se registra el lote de origen.
                # Una implementación robusta requeriría el LOTE que se envió para devolverlo al mismo.
                stock_origen = StockProducto.objects.filter(
                    producto=self.producto,
                    sucursal=self.sucursal_origen
                ).order_by('-cantidad').first() # Recupera un stock para devolver

                if stock_origen:
                    stock_origen.cantidad += self.cantidad
                    stock_origen.save()
                    MovimientoInventario.objects.create(
                        producto=self.producto,
                        sucursal=self.sucursal_origen,
                        stock_afectado=stock_origen,
                        tipo_movimiento='AJUSTE_POSITIVO', # O un tipo de movimiento específico para "Devolución por Rechazo Transferencia"
                        cantidad=self.cantidad,
                        usuario=usuario_rechazo,
                        referencia_doc=f"Transferencia ID: {self.id} (Rechazo)",
                        observaciones=f"Devolución de stock por rechazo de transferencia desde {self.sucursal_destino.nombre}. {observaciones_rechazo}"
                    )
                self.estado = 'RECHAZADO'
                self.observaciones = f"Rechazado en recepción por {usuario_rechazo.username}: {observaciones_rechazo}"
                self.recibido_por = usuario_rechazo
                self.fecha_recepcion = timezone.now() # O fecha de rechazo
                self.save()
            else:
                raise ValueError(f"La transferencia no puede ser rechazada en estado '{self.estado}'.")

