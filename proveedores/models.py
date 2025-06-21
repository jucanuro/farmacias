# proveedores/models.py

from django.db import models

class Proveedor(models.Model):
    """
    Información detallada de los proveedores que suministran productos
    a la cadena de farmacias.
    """
    TIPO_DOCUMENTO_CHOICES = [
        ('RUC', 'Registro Único de Contribuyentes'), # Perú
        ('NIT', 'Número de Identificación Tributaria'), # Colombia, Guatemala
        ('TAX_ID', 'Tax ID / EIN'), # Estados Unidos
        ('CIF', 'Certificado de Identificación Fiscal'), # España
        ('OTRO', 'Otro'),
    ]

    nombre_comercial = models.CharField(max_length=200, verbose_name="Nombre Comercial del Proveedor")
    razon_social = models.CharField(max_length=255, unique=True, verbose_name="Razón Social")
    tipo_documento = models.CharField(
        max_length=20, choices=TIPO_DOCUMENTO_CHOICES, default='RUC',
        verbose_name="Tipo de Documento Fiscal"
    )
    numero_documento = models.CharField(
        max_length=50, unique=True,
        verbose_name="Número de Documento Fiscal",
        help_text="Número de identificación fiscal o tributaria del proveedor."
    )
    direccion = models.CharField(max_length=255, blank=True, verbose_name="Dirección Principal")
    telefono = models.CharField(max_length=20, blank=True, verbose_name="Teléfono Principal")
    email = models.EmailField(max_length=255, blank=True, verbose_name="Email de Contacto")
    sitio_web = models.URLField(max_length=255, blank=True, verbose_name="Sitio Web")
    persona_contacto = models.CharField(max_length=100, blank=True, verbose_name="Persona de Contacto")
    telefono_contacto = models.CharField(max_length=20, blank=True, verbose_name="Teléfono de Contacto Adicional")
    condiciones_pago = models.TextField(blank=True, verbose_name="Condiciones de Pago Estandar")
    activo = models.BooleanField(default=True, verbose_name="Activo",
                                 help_text="Indica si el proveedor está activo y puede usarse para compras.")
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Registro")

    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
        ordering = ['nombre_comercial'] # Ordenar alfabéticamente por nombre comercial

    def __str__(self):
        return self.nombre_comercial
