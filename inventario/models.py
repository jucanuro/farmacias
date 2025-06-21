# inventario/models.py

from django.db import models
from core.models import Sucursal, Usuario # Importar Sucursal y Usuario de la app 'core'

# --- Modelos de Maestros de Productos ---
class CategoriaProducto(models.Model):
    """Categorías para organizar los productos (ej. Analgésicos, Antibióticos, Cosméticos)."""
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre de Categoría")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")

    class Meta:
        verbose_name = "Categoría de Producto"
        verbose_name_plural = "Categorías de Productos"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

class Laboratorio(models.Model):
    """Representa el laboratorio o fabricante de un producto."""
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre del Laboratorio")
    direccion = models.CharField(max_length=255, blank=True, verbose_name="Dirección")
    telefono = models.CharField(max_length=20, blank=True, verbose_name="Teléfono")
    email = models.EmailField(max_length=255, blank=True, verbose_name="Email de Contacto") # <-- ¡CAMPO AÑADIDO!

    class Meta:
        verbose_name = "Laboratorio"
        verbose_name_plural = "Laboratorios"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

class PrincipioActivo(models.Model):
    """El componente químico activo de un medicamento."""
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre del Principio Activo")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")

    class Meta:
        verbose_name = "Principio Activo"
        verbose_name_plural = "Principios Activos"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

class FormaFarmaceutica(models.Model):
    """La forma en que se presenta un medicamento (ej. Tableta, Jarabe, Crema)."""
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre de Forma Farmacéutica")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")

    class Meta:
        verbose_name = "Forma Farmacéutica"
        verbose_name_plural = "Formas Farmacéuticas"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    """
    Define un producto general con sus características.
    El stock se maneja a nivel de StockProducto para cada sucursal y lote.
    """
    UNIDAD_MEDIDA_CHOICES = [
        ('unidad', 'Unidad'),
        ('ml', 'Mililitros (ml)'),
        ('g', 'Gramos (g)'),
        ('mg', 'Miligramos (mg)'),
        ('l', 'Litros (l)'),
    ]
    PRESENTACION_BASE_CHOICES = [
        ('caja', 'Caja'),
        ('blister', 'Blíster'),
        ('unidad', 'Unidad'), # Para productos que se venden sueltos o a granel
        ('frasco', 'Frasco'),
        ('tubo', 'Tubo'),
    ]

    nombre = models.CharField(max_length=200, verbose_name="Nombre del Producto")
    descripcion = models.TextField(blank=True, verbose_name="Descripción Detallada")
    codigo_barras = models.CharField(
        max_length=100, unique=True, blank=True, null=True,
        verbose_name="Código de Barras (EAN)",
        help_text="Código de barras EAN o similar para el producto."
    )
    principio_activo = models.ForeignKey(
        PrincipioActivo, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name="Principio Activo"
    )
    concentracion = models.CharField(max_length=100, blank=True, verbose_name="Concentración (ej. 500mg)")
    forma_farmaceutica = models.ForeignKey(
        FormaFarmaceutica, on_delete=models.PROTECT, # No borrar si hay productos asociados
        verbose_name="Forma Farmacéutica"
    )
    laboratorio = models.ForeignKey(
        Laboratorio, on_delete=models.PROTECT, # No borrar si hay productos asociados
        verbose_name="Laboratorio"
    )
    categoria = models.ForeignKey(
        CategoriaProducto, on_delete=models.PROTECT, # No borrar si hay productos asociados
        verbose_name="Categoría"
    )
    presentacion_base = models.CharField(
        max_length=50, choices=PRESENTACION_BASE_CHOICES,
        verbose_name="Presentación Base",
        help_text="Unidad en la que el producto se compra/almacena (ej. Caja, Blíster)."
    )
    cantidad_por_presentacion_base = models.DecimalField(
        max_digits=10, decimal_places=2, default=1,
        verbose_name="Unidades por Presentación Base",
        help_text="Ej: Para una 'caja' de 100 pastillas, este valor es 100. Para un 'blister' de 10, es 10."
    )
    unidad_medida = models.CharField(
        max_length=20, choices=UNIDAD_MEDIDA_CHOICES,
        verbose_name="Unidad de Medida",
        help_text="La unidad que representa la 'cantidad_por_presentacion_base' (ej. unidad, ml, g)."
    )
    precio_compra_promedio = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00,
        verbose_name="Precio de Compra Promedio",
        help_text="Precio de compra promedio del producto en su presentación base."
    )
    margen_ganancia_sugerido = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.20, # 20%
        verbose_name="Margen de Ganancia Sugerido (%)",
        help_text="Ej: 0.20 para 20% de margen."
    )
    aplica_receta = models.BooleanField(default=False, verbose_name="Requiere Receta Médica",
                                        help_text="Marca si el producto necesita receta para su venta.")
    es_controlado = models.BooleanField(default=False, verbose_name="Es Producto Controlado",
                                        help_text="Marca si es un producto controlado (estupefacientes/psicotrópicos).")
    imagen_producto = models.ImageField(upload_to='productos/', blank=True, null=True, verbose_name="Imagen del Producto")
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Registro")

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} - {self.concentracion} ({self.presentacion_base})"

    def get_precio_venta_sugerido(self):
        """Calcula el precio de venta sugerido basado en el precio de compra y el margen."""
        return self.precio_compra_promedio * (1 + self.margen_ganancia_sugerido)


class StockProducto(models.Model):
    """
    Representa el stock de un producto específico en una sucursal,
    diferenciado por lote y fecha de vencimiento.
    Este modelo es CRÍTICO para el inventario descentralizado por sucursal.
    """
    producto = models.ForeignKey(
        Producto, on_delete=models.CASCADE,
        verbose_name="Producto"
    )
    sucursal = models.ForeignKey(
        Sucursal, on_delete=models.CASCADE,
        verbose_name="Sucursal"
    )
    lote = models.CharField(max_length=50, verbose_name="Número de Lote")
    fecha_vencimiento = models.DateField(verbose_name="Fecha de Vencimiento")
    cantidad = models.IntegerField(default=0, verbose_name="Cantidad Disponible",
                                   help_text="Cantidad del producto en su 'presentación base' (ej. número de cajas).")
    ubicacion_almacen = models.CharField(max_length=100, blank=True, verbose_name="Ubicación en Almacén",
                                         help_text="Ej: 'Estantería A1', 'Refrigerador'."
    )
    ultima_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")

    class Meta:
        verbose_name = "Stock de Producto"
        verbose_name_plural = "Stocks de Productos"
        unique_together = ('producto', 'sucursal', 'lote')
        ordering = ['sucursal__nombre', 'producto__nombre', 'fecha_vencimiento']

    def __str__(self):
        return (
            f"{self.producto.nombre} ({self.lote}) - "
            f"Sucursal: {self.sucursal.nombre} - Cantidad: {self.cantidad}"
        )


class MovimientoInventario(models.Model):
    """
    Registra cada entrada, salida o ajuste de stock, proporcionando una trazabilidad completa.
    """
    TIPO_MOVIMIENTO_CHOICES = [
        ('ENTRADA', 'Entrada (Compra, Devolución Cliente, Transferencia Recibida)'),
        ('SALIDA', 'Salida (Venta, Merma, Transferencia Enviada, Devolución a Proveedor)'),
        ('AJUSTE_POSITIVO', 'Ajuste Positivo (Inventario Físico)'),
        ('AJUSTE_NEGATIVO', 'Ajuste Negativo (Inventario Físico)'),
    ]

    producto = models.ForeignKey(
        Producto, on_delete=models.PROTECT,
        verbose_name="Producto Afectado"
    )
    sucursal = models.ForeignKey(
        Sucursal, on_delete=models.PROTECT,
        verbose_name="Sucursal del Movimiento"
    )
    stock_afectado = models.ForeignKey(
        StockProducto, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name="Stock de Producto Afectado",
        help_text="Referencia al registro de StockProducto específico (lote/vencimiento) afectado."
    )
    tipo_movimiento = models.CharField(
        max_length=50, choices=TIPO_MOVIMIENTO_CHOICES,
        verbose_name="Tipo de Movimiento"
    )
    cantidad = models.IntegerField(verbose_name="Cantidad del Movimiento")
    fecha_movimiento = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y Hora del Movimiento")
    usuario = models.ForeignKey(
        Usuario, on_delete=models.PROTECT,
        verbose_name="Usuario que realizó el movimiento"
    )
    referencia_doc = models.CharField(
        max_length=100, blank=True,
        verbose_name="Referencia de Documento",
        help_text="ID de Venta, ID de Compra, ID de Transferencia, etc."
    )
    observaciones = models.TextField(blank=True, verbose_name="Observaciones Adicionales")

    class Meta:
        verbose_name = "Movimiento de Inventario"
        verbose_name_plural = "Movimientos de Inventario"
        ordering = ['-fecha_movimiento'] # Ordenar por fecha descendente

    def __str__(self):
        return (
            f"{self.tipo_movimiento} de {self.cantidad} de {self.producto.nombre} "
            f"en {self.sucursal.nombre} ({self.fecha_movimiento.strftime('%Y-%m-%d %H:%M')})"
        )
