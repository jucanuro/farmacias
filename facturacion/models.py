# facturacion/models.py

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone


class SerieComprobante(models.Model):
    TIPO_COMPROBANTE_CHOICES = [
        ("01", "Factura Electrónica"),
        ("03", "Boleta de Venta Electrónica"),
        ("07", "Nota de Crédito Electrónica"),
        ("08", "Nota de Débito Electrónica"),
    ]

    AMBIENTE_CHOICES = [
        ("BETA", "Beta / Pruebas"),
        ("PRODUCCION", "Producción"),
    ]

    sucursal = models.ForeignKey(
        "core.Sucursal",
        on_delete=models.PROTECT,
        related_name="series_comprobantes"
    )
    tipo_comprobante = models.CharField(
        max_length=2,
        choices=TIPO_COMPROBANTE_CHOICES
    )
    serie = models.CharField(max_length=4)
    correlativo_actual = models.PositiveIntegerField(default=0)
    ambiente = models.CharField(
        max_length=20,
        choices=AMBIENTE_CHOICES,
        default="BETA"
    )
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Serie de Comprobante"
        verbose_name_plural = "Series de Comprobantes"
        unique_together = ("sucursal", "tipo_comprobante", "serie", "ambiente")
        ordering = ["sucursal", "tipo_comprobante", "serie"]

    def __str__(self):
        return f"{self.serie} - {self.get_tipo_comprobante_display()}"

    def siguiente_numero(self):
        self.correlativo_actual += 1
        self.save(update_fields=["correlativo_actual"])
        return self.correlativo_actual


class ComprobanteElectronico(models.Model):
    TIPO_COMPROBANTE_CHOICES = [
        ("01", "Factura Electrónica"),
        ("03", "Boleta de Venta Electrónica"),
        ("07", "Nota de Crédito Electrónica"),
        ("08", "Nota de Débito Electrónica"),
    ]

    ESTADO_CHOICES = [
        ("BORRADOR", "Borrador"),
        ("PENDIENTE", "Pendiente de Envío"),
        ("GENERADO", "XML Generado"),
        ("FIRMADO", "XML Firmado"),
        ("ENVIADO", "Enviado a SUNAT/OSE"),
        ("ACEPTADO", "Aceptado"),
        ("ACEPTADO_OBSERVADO", "Aceptado con Observaciones"),
        ("RECHAZADO", "Rechazado"),
        ("ERROR", "Error"),
        ("ANULADO", "Anulado"),
    ]

    AMBIENTE_CHOICES = [
        ("BETA", "Beta / Pruebas"),
        ("PRODUCCION", "Producción"),
    ]

    MONEDA_CHOICES = [
        ("PEN", "Soles"),
        ("USD", "Dólares"),
    ]

    venta = models.OneToOneField(
        "ventas.Venta",
        on_delete=models.PROTECT,
        related_name="comprobante_electronico"
    )

    serie_comprobante = models.ForeignKey(
        SerieComprobante,
        on_delete=models.PROTECT,
        related_name="comprobantes"
    )

    tipo_comprobante = models.CharField(
        max_length=2,
        choices=TIPO_COMPROBANTE_CHOICES
    )
    serie = models.CharField(max_length=4)
    numero = models.PositiveIntegerField()
    codigo_hash = models.CharField(max_length=255, blank=True, null=True)

    ambiente = models.CharField(
        max_length=20,
        choices=AMBIENTE_CHOICES,
        default="BETA"
    )
    estado = models.CharField(
        max_length=30,
        choices=ESTADO_CHOICES,
        default="PENDIENTE"
    )

    moneda = models.CharField(
        max_length=3,
        choices=MONEDA_CHOICES,
        default="PEN"
    )

    fecha_emision = models.DateTimeField(default=timezone.now)
    fecha_envio = models.DateTimeField(blank=True, null=True)
    fecha_respuesta = models.DateTimeField(blank=True, null=True)

    ruc_emisor = models.CharField(max_length=11)
    razon_social_emisor = models.CharField(max_length=255)
    nombre_comercial_emisor = models.CharField(max_length=255, blank=True)
    direccion_emisor = models.CharField(max_length=255, blank=True)
    ubigeo_emisor = models.CharField(max_length=6, blank=True)

    tipo_documento_cliente = models.CharField(max_length=2, blank=True)
    numero_documento_cliente = models.CharField(max_length=20, blank=True)
    nombre_cliente = models.CharField(max_length=255, blank=True)
    direccion_cliente = models.CharField(max_length=255, blank=True)
    email_cliente = models.EmailField(blank=True)

    total_gravado = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_exonerado = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_inafecto = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_igv = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_descuentos = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_importe = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    xml_nombre = models.CharField(max_length=255, blank=True)
    xml_firmado = models.TextField(blank=True)
    zip_base64 = models.TextField(blank=True)
    cdr_base64 = models.TextField(blank=True)

    sunat_ticket = models.CharField(max_length=100, blank=True)
    sunat_codigo_respuesta = models.CharField(max_length=20, blank=True)
    sunat_descripcion = models.TextField(blank=True)
    sunat_notas = models.TextField(blank=True)

    intentos_envio = models.PositiveIntegerField(default=0)
    ultimo_error = models.TextField(blank=True)

    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="comprobantes_creados",
        blank=True,
        null=True
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Comprobante Electrónico"
        verbose_name_plural = "Comprobantes Electrónicos"
        unique_together = ("tipo_comprobante", "serie", "numero", "ambiente")
        ordering = ["-fecha_emision"]

    def __str__(self):
        return f"{self.serie}-{self.numero:08d}"

    @property
    def numero_formateado(self):
        return f"{self.serie}-{self.numero:08d}"

    @property
    def nombre_archivo_sunat(self):
        return f"{self.ruc_emisor}-{self.tipo_comprobante}-{self.numero_formateado}"

    def clean(self):
        if self.tipo_comprobante == "01" and not self.numero_documento_cliente:
            raise ValidationError("La factura requiere datos del cliente.")

        if self.tipo_comprobante == "01" and self.tipo_documento_cliente != "6":
            raise ValidationError("La factura electrónica debe emitirse a cliente con RUC.")

        if self.tipo_comprobante == "03" and not self.serie.startswith("B"):
            raise ValidationError("La serie de boleta electrónica debe iniciar con B.")

        if self.tipo_comprobante == "01" and not self.serie.startswith("F"):
            raise ValidationError("La serie de factura electrónica debe iniciar con F.")


class ComprobanteElectronicoDetalle(models.Model):
    comprobante = models.ForeignKey(
        ComprobanteElectronico,
        on_delete=models.CASCADE,
        related_name="detalles"
    )
    detalle_venta = models.ForeignKey(
        "ventas.DetalleVenta",
        on_delete=models.PROTECT,
        related_name="detalle_facturacion"
    )

    producto_codigo = models.CharField(max_length=50, blank=True)
    producto_nombre = models.CharField(max_length=255)
    unidad_medida = models.CharField(max_length=10, default="NIU")

    cantidad = models.DecimalField(max_digits=12, decimal_places=2)
    valor_unitario = models.DecimalField(max_digits=12, decimal_places=6)
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=6)
    descuento = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    valor_venta = models.DecimalField(max_digits=12, decimal_places=2)
    igv = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_linea = models.DecimalField(max_digits=12, decimal_places=2)

    codigo_tipo_afectacion_igv = models.CharField(max_length=2, default="10")

    class Meta:
        verbose_name = "Detalle de Comprobante Electrónico"
        verbose_name_plural = "Detalles de Comprobante Electrónico"

    def __str__(self):
        return f"{self.producto_nombre} - {self.cantidad}"


class ResumenDiarioBoletas(models.Model):
    ESTADO_CHOICES = [
        ("PENDIENTE", "Pendiente"),
        ("ENVIADO", "Enviado"),
        ("ACEPTADO", "Aceptado"),
        ("RECHAZADO", "Rechazado"),
        ("ERROR", "Error"),
    ]

    sucursal = models.ForeignKey(
        "core.Sucursal",
        on_delete=models.PROTECT,
        related_name="resumenes_boletas"
    )
    fecha_resumen = models.DateField()
    correlativo = models.PositiveIntegerField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default="PENDIENTE")

    ticket_sunat = models.CharField(max_length=100, blank=True)
    xml_firmado = models.TextField(blank=True)
    zip_base64 = models.TextField(blank=True)
    cdr_base64 = models.TextField(blank=True)

    sunat_codigo_respuesta = models.CharField(max_length=20, blank=True)
    sunat_descripcion = models.TextField(blank=True)
    ultimo_error = models.TextField(blank=True)

    fecha_envio = models.DateTimeField(blank=True, null=True)
    fecha_respuesta = models.DateTimeField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Resumen Diario de Boletas"
        verbose_name_plural = "Resúmenes Diarios de Boletas"
        unique_together = ("sucursal", "fecha_resumen", "correlativo")
        ordering = ["-fecha_resumen", "-correlativo"]

    def __str__(self):
        return f"RC-{self.fecha_resumen.strftime('%Y%m%d')}-{self.correlativo}"


class ResumenDiarioBoletaDetalle(models.Model):
    resumen = models.ForeignKey(
        ResumenDiarioBoletas,
        on_delete=models.CASCADE,
        related_name="detalles"
    )
    comprobante = models.ForeignKey(
        ComprobanteElectronico,
        on_delete=models.PROTECT,
        related_name="resumenes_diarios"
    )

    estado_item = models.CharField(
        max_length=1,
        choices=[
            ("1", "Adicionar"),
            ("2", "Modificar"),
            ("3", "Anulado"),
        ],
        default="1"
    )

    class Meta:
        verbose_name = "Detalle de Resumen Diario"
        verbose_name_plural = "Detalles de Resumen Diario"
        unique_together = ("resumen", "comprobante")

    def __str__(self):
        return f"{self.resumen} - {self.comprobante}"


class EventoComprobanteElectronico(models.Model):
    comprobante = models.ForeignKey(
        ComprobanteElectronico,
        on_delete=models.CASCADE,
        related_name="eventos"
    )
    estado_anterior = models.CharField(max_length=30, blank=True)
    estado_nuevo = models.CharField(max_length=30)
    descripcion = models.TextField(blank=True)
    respuesta_sunat = models.TextField(blank=True)
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Evento de Comprobante Electrónico"
        verbose_name_plural = "Eventos de Comprobantes Electrónicos"
        ordering = ["-fecha_creacion"]

    def __str__(self):
        return f"{self.comprobante} → {self.estado_nuevo}"