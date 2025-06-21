# core/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser

# --- Modelos de Autenticación y Usuarios ---
class Rol(models.Model):
    """
    Define los roles de usuario en el sistema, como 'Administrador de Farmacia',
    'Gerente de Sucursal', 'Vendedor', etc.
    """
    nombre = models.CharField(max_length=50, unique=True, verbose_name="Nombre del Rol")
    descripcion = models.TextField(blank=True, verbose_name="Descripción del Rol")

    class Meta:
        verbose_name = "Rol"
        verbose_name_plural = "Roles" # <-- CORREGIDO AQUÍ
        ordering = ['nombre'] # Ordenar alfabéticamente por nombre

    def __str__(self):
        return self.nombre

class Usuario(AbstractUser):
    """
    Modelo de usuario personalizado que extiende AbstractUser de Django.
    Añade campos para asociar el usuario a una Farmacia, Sucursal y Rol específico.
    """
    farmacia = models.ForeignKey(
        'Farmacia',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Farmacia Asociada",
        help_text="Farmacia a la que pertenece este usuario (si aplica). Un superusuario no necesita estar asociado."
    )
    sucursal = models.ForeignKey(
        'Sucursal',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Sucursal Asociada",
        help_text="Sucursal a la que está asignado este usuario (si aplica). Un gerente de sucursal o vendedor se asignaría aquí."
    )
    rol = models.ForeignKey(
        Rol,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Rol del Usuario",
        help_text="Rol principal del usuario en el sistema, define sus permisos y acceso."
    )

    class Meta:
        verbose_name = "Usuario del Sistema"
        verbose_name_plural = "Usuarios del Sistema" # <-- CORREGIDO AQUÍ
        # AbstractUser ya maneja la unicidad del username

    def __str__(self):
        return self.username # Retorna el nombre de usuario

# --- Modelos de Estructura de Farmacias ---
class ConfiguracionFacturacionElectronica(models.Model):
    """
    Almacena la configuración necesaria para la integración con servicios
    de Facturación Electrónica específicos de cada país (ej. SUNAT, AFIP, SII).
    """
    api_key = models.CharField(max_length=255, blank=True, verbose_name="API Key")
    api_secret = models.CharField(max_length=255, blank=True, verbose_name="API Secret")
    url_base_api = models.URLField(max_length=255, blank=True, verbose_name="URL Base de la API de FE")
    certificado_pem = models.TextField(blank=True, verbose_name="Contenido del Certificado .PEM (Base64/Texto)",
                                      help_text="Contenido del archivo .PEM o .P12 convertido a Base64/Texto.")
    clave_certificado = models.CharField(max_length=255, blank=True, verbose_name="Clave del Certificado",
                                       help_text="Clave para acceder al certificado de facturación.")
    modo_produccion = models.BooleanField(default=False, verbose_name="Modo Producción Activo",
                                          help_text="Si está activo, las facturas se enviarán a producción, de lo contrario a entorno de pruebas.")
    ruc_emisor = models.CharField(max_length=20, blank=True, verbose_name="RUC del Emisor")
    nombre_emisor = models.CharField(max_length=255, blank=True, verbose_name="Nombre/Razón Social del Emisor")

    class Meta:
        verbose_name = "Configuración Facturación Electrónica"
        verbose_name_plural = "Configuraciones de Facturación Electrónica" # <-- CORREGIDO AQUÍ

    def __str__(self):
        return f"Configuración FE para {self.ruc_emisor or 'Sin RUC'}"


class Farmacia(models.Model):
    """
    Representa una cadena de farmacias o una farmacia principal.
    Es el nivel superior de organización que agrupa a sus sucursales.
    Cada farmacia gestiona su propio inventario a través de sus sucursales.
    """
    nombre = models.CharField(max_length=200, verbose_name="Nombre de la Farmacia/Cadena")
    razon_social = models.CharField(max_length=255, verbose_name="Razón Social")
    ruc = models.CharField(max_length=20, unique=True, verbose_name="RUC/Identificación Fiscal")
    direccion = models.CharField(max_length=255, blank=True, verbose_name="Dirección Principal")
    telefono = models.CharField(max_length=20, blank=True, verbose_name="Teléfono Principal")
    email = models.EmailField(max_length=255, blank=True, verbose_name="Email Principal")
    logo = models.ImageField(upload_to='logos_farmacias/', blank=True, null=True, verbose_name="Logo de la Farmacia",
                             help_text="Sube el logo de la cadena de farmacias.")
    configuracion_facturacion_electronica = models.OneToOneField(
        ConfiguracionFacturacionElectronica,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Configuración FE Asociada",
        help_text="Configuración de facturación electrónica específica para esta farmacia."
    )
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Registro")

    class Meta:
        verbose_name = "Farmacia"
        verbose_name_plural = "Farmacias" # <-- CORREGIDO AQUÍ
        ordering = ['nombre'] # Ordenar alfabéticamente por nombre

    def __str__(self):
        return self.nombre


class Sucursal(models.Model):
    """
    Representa una sucursal individual que pertenece a una Farmacia.
    Los inventarios se gestionan a nivel de sucursal.
    """
    farmacia = models.ForeignKey(
        Farmacia,
        on_delete=models.CASCADE, # Si la farmacia se elimina, sus sucursales también
        related_name='sucursales',
        verbose_name="Farmacia a la que pertenece",
        help_text="La cadena de farmacias o farmacia principal a la que pertenece esta sucursal."
    )
    nombre = models.CharField(max_length=200, verbose_name="Nombre de la Sucursal")
    codigo = models.CharField(max_length=10, unique=True, verbose_name="Código de Sucursal",
                              help_text="Código corto y único para identificar la sucursal (ej. 'SUR01', 'CENTRO').")
    direccion = models.CharField(max_length=255, blank=True, verbose_name="Dirección de la Sucursal")
    telefono = models.CharField(max_length=20, blank=True, verbose_name="Teléfono de la Sucursal")
    administrador = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sucursales_administradas',
        verbose_name="Administrador de Sucursal",
        help_text="Usuario responsable de la gestión de esta sucursal."
    )
    fecha_apertura = models.DateField(null=True, blank=True, verbose_name="Fecha de Apertura")

    class Meta:
        verbose_name = "Sucursal"
        verbose_name_plural = "Sucursales" # <-- CORREGIDO AQUÍ
        # Asegurarse de que no haya dos sucursales con el mismo código en la misma farmacia (aunque 'unique=True' ya lo hace global)
        unique_together = ('farmacia', 'codigo') # Un código de sucursal debe ser único dentro de una farmacia
        ordering = ['farmacia__nombre', 'nombre'] # Ordenar por farmacia y luego por nombre de sucursal

    def __str__(self):
        return f"{self.nombre} ({self.farmacia.nombre})"

