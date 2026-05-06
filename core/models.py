from django.db import models
from django.contrib.auth.models import AbstractUser


class Rol(models.Model):
    nombre = models.CharField(max_length=50, unique=True, verbose_name="Nombre del Rol")
    descripcion = models.TextField(blank=True, verbose_name="Descripción del Rol")

    class Meta:
        verbose_name = "Rol"
        verbose_name_plural = "Roles"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Usuario(AbstractUser):
    farmacia = models.ForeignKey(
        'Farmacia',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Farmacia Asociada"
    )
    sucursal = models.ForeignKey(
        'Sucursal',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Sucursal Asociada"
    )
    rol = models.ForeignKey(
        Rol,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Rol del Usuario"
    )

    class Meta:
        verbose_name = "Usuario del Sistema"
        verbose_name_plural = "Usuarios del Sistema"

    def __str__(self):
        nombre_completo = self.get_full_name()
        return nombre_completo if nombre_completo else self.username


class ConfiguracionFacturacionElectronica(models.Model):
    api_key = models.CharField(max_length=255, blank=True, verbose_name="API Key")
    api_secret = models.CharField(max_length=255, blank=True, verbose_name="API Secret")
    url_base_api = models.URLField(max_length=255, blank=True, verbose_name="URL Base de la API de FE")
    certificado_pem = models.TextField(blank=True, verbose_name="Contenido del Certificado .PEM")
    clave_certificado = models.CharField(max_length=255, blank=True, verbose_name="Clave del Certificado")
    modo_produccion = models.BooleanField(default=False, verbose_name="Modo Producción Activo")
    ruc_emisor = models.CharField(max_length=20, blank=True, verbose_name="RUC del Emisor")
    nombre_emisor = models.CharField(max_length=255, blank=True, verbose_name="Nombre/Razón Social del Emisor")

    class Meta:
        verbose_name = "Configuración Facturación Electrónica"
        verbose_name_plural = "Configuraciones de Facturación Electrónica"

    def __str__(self):
        return f"Configuración FE para {self.ruc_emisor or 'Sin RUC'}"


class Farmacia(models.Model):
    nombre = models.CharField(max_length=200, verbose_name="Nombre de la Farmacia/Cadena")
    razon_social = models.CharField(max_length=255, verbose_name="Razón Social")
    ruc = models.CharField(max_length=20, unique=True, verbose_name="RUC/Identificación Fiscal")
    direccion = models.CharField(max_length=255, blank=True, verbose_name="Dirección Principal")
    telefono = models.CharField(max_length=20, blank=True, verbose_name="Teléfono Principal")
    email = models.EmailField(max_length=255, blank=True, verbose_name="Email Principal")
    logo = models.ImageField(upload_to='logos_farmacias/', blank=True, null=True, verbose_name="Logo de la Farmacia")
    configuracion_facturacion_electronica = models.OneToOneField(
        ConfiguracionFacturacionElectronica,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Configuración FE Asociada"
    )
    activo = models.BooleanField(default=True, verbose_name="Activa")
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Registro")

    class Meta:
        verbose_name = "Farmacia"
        verbose_name_plural = "Farmacias"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Sucursal(models.Model):
    farmacia = models.ForeignKey(
        Farmacia,
        on_delete=models.CASCADE,
        related_name='sucursales',
        verbose_name="Farmacia a la que pertenece"
    )
    nombre = models.CharField(max_length=200, verbose_name="Nombre de la Sucursal")
    codigo = models.CharField(max_length=10, unique=True, verbose_name="Código de Sucursal")
    direccion = models.CharField(max_length=255, blank=True, verbose_name="Dirección de la Sucursal")
    telefono = models.CharField(max_length=20, blank=True, verbose_name="Teléfono de la Sucursal")
    administrador = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sucursales_administradas',
        verbose_name="Administrador de Sucursal"
    )
    fecha_apertura = models.DateField(null=True, blank=True, verbose_name="Fecha de Apertura")

    class Meta:
        verbose_name = "Sucursal"
        verbose_name_plural = "Sucursales"
        unique_together = ('farmacia', 'codigo')
        ordering = ['farmacia__nombre', 'nombre']

    def __str__(self):
        return f"{self.nombre} ({self.farmacia.nombre})"
    
    
class SerieComprobante(models.Model):
    TIPO_COMPROBANTE_CHOICES = [
        ("01", "Factura Electrónica"),
        ("03", "Boleta de Venta Electrónica"),
    ]

    AMBIENTE_CHOICES = [
        ("BETA", "Beta / Pruebas"),
        ("PRODUCCION", "Producción"),
    ]

    farmacia = models.ForeignKey(
        Farmacia,
        on_delete=models.PROTECT,
        related_name="series_comprobantes",
        verbose_name="Farmacia"
    )
    sucursal = models.ForeignKey(
        Sucursal,
        on_delete=models.PROTECT,
        related_name="series_comprobantes",
        verbose_name="Sucursal"
    )
    tipo_comprobante = models.CharField(
        max_length=2,
        choices=TIPO_COMPROBANTE_CHOICES,
        verbose_name="Tipo de Comprobante"
    )
    serie = models.CharField(
        max_length=4,
        verbose_name="Serie"
    )
    correlativo_actual = models.PositiveIntegerField(
        default=0,
        verbose_name="Último correlativo usado"
    )
    ambiente = models.CharField(
        max_length=20,
        choices=AMBIENTE_CHOICES,
        default="BETA",
        verbose_name="Ambiente"
    )
    activo = models.BooleanField(
        default=True,
        verbose_name="Activo"
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación"
    )

    class Meta:
        verbose_name = "Serie de Comprobante"
        verbose_name_plural = "Series de Comprobantes"
        unique_together = (
            "farmacia",
            "sucursal",
            "tipo_comprobante",
            "serie",
            "ambiente",
        )
        ordering = ["farmacia", "sucursal", "tipo_comprobante", "serie"]

    def __str__(self):
        return f"{self.sucursal.nombre} - {self.serie}-{self.correlativo_actual:08d}"

    @property
    def siguiente_correlativo_preview(self):
        return f"{self.serie}-{self.correlativo_actual + 1:08d}"

    def clean(self):
        if self.sucursal and self.farmacia and self.sucursal.farmacia_id != self.farmacia_id:
            from django.core.exceptions import ValidationError
            raise ValidationError("La sucursal seleccionada no pertenece a esta farmacia.")

        if self.tipo_comprobante == "01" and not self.serie.startswith("F"):
            from django.core.exceptions import ValidationError
            raise ValidationError("La serie de factura debe iniciar con F. Ejemplo: F001.")

        if self.tipo_comprobante == "03" and not self.serie.startswith("B"):
            from django.core.exceptions import ValidationError
            raise ValidationError("La serie de boleta debe iniciar con B. Ejemplo: B001.")