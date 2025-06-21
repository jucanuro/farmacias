# clientes/models.py

from django.db import models
from core.models import Farmacia # Importa el modelo Farmacia de la app 'core'

class Cliente(models.Model):
    """
    Información detallada de un cliente. Puede estar asociado a una farmacia principal
    si se desea segmentar o para programas de fidelización específicos de una cadena.
    """
    TIPO_DOCUMENTO_CHOICES = [
        ('DNI', 'Documento Nacional de Identidad'),
        ('RUC', 'Registro Único de Contribuyentes'),
        ('PASAPORTE', 'Pasaporte'),
        ('CE', 'Carnet de Extranjería'), # Para extranjeros residentes en Perú
        ('OTRO', 'Otro'),
    ]

    farmacia = models.ForeignKey(
        Farmacia, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name="Farmacia Principal del Cliente",
        help_text="Farmacia principal a la que este cliente está asociado (opcional)."
    )
    tipo_documento = models.CharField(
        max_length=20, choices=TIPO_DOCUMENTO_CHOICES, default='DNI',
        verbose_name="Tipo de Documento"
    )
    numero_documento = models.CharField(
        max_length=20, unique=True,
        verbose_name="Número de Documento",
        help_text="Número de identificación del cliente (DNI, RUC, etc.)."
    )
    nombres = models.CharField(max_length=100, verbose_name="Nombres")
    apellidos = models.CharField(max_length=100, blank=True, verbose_name="Apellidos")
    direccion = models.CharField(max_length=255, blank=True, verbose_name="Dirección")
    telefono = models.CharField(max_length=20, blank=True, verbose_name="Teléfono")
    email = models.EmailField(max_length=255, blank=True, verbose_name="Email")
    fecha_nacimiento = models.DateField(null=True, blank=True, verbose_name="Fecha de Nacimiento")
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Registro")
    activo = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['apellidos', 'nombres'] # Ordenar por apellido y luego por nombre

    def __str__(self):
        return f"{self.nombres} {self.apellidos} ({self.numero_documento})"

    def get_full_name(self):
        """Retorna el nombre completo del cliente."""
        return f"{self.nombres} {self.apellidos}".strip()

