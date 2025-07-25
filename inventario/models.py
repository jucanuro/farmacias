from django.db import models
from core.models import Sucursal, Usuario

# --- Modelos de Maestros de Productos (Definidos ANTES que Producto) ---

class CategoriaProducto(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre de Categoría")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    class Meta:
        verbose_name = "Categoría de Producto"
        verbose_name_plural = "Categorías de Productos"
        ordering = ['nombre']
    def __str__(self):
        return self.nombre

class Laboratorio(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre del Laboratorio")
    direccion = models.CharField(max_length=255, blank=True, verbose_name="Dirección")
    telefono = models.CharField(max_length=20, blank=True, verbose_name="Teléfono")
    email = models.EmailField(max_length=255, blank=True, verbose_name="Email de Contacto")
    class Meta:
        verbose_name = "Laboratorio"
        verbose_name_plural = "Laboratorios"
        ordering = ['nombre']
    def __str__(self):
        return self.nombre

class PrincipioActivo(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre del Principio Activo")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    class Meta:
        verbose_name = "Principio Activo"
        verbose_name_plural = "Principios Activos"
        ordering = ['nombre']
    def __str__(self):
        return self.nombre

class FormaFarmaceutica(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre de Forma Farmacéutica")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    class Meta:
        verbose_name = "Forma Farmacéutica"
        verbose_name_plural = "Formas Farmacéuticas"
        ordering = ['nombre']
    def __str__(self):
        return self.nombre

class UnidadPresentacion(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre de la Unidad")
    padre = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='hijos', verbose_name="Unidad Contenedora (Padre)")
    factor_conversion = models.PositiveIntegerField(default=1, verbose_name="Cantidad Contenida en el Padre", help_text="Ej: Si esta unidad es 'Blister' y el padre es 'Caja', y hay 10 blisters en una caja, el factor es 10.")
    class Meta:
        verbose_name = "Unidad de Presentación"
        verbose_name_plural = "Unidades de Presentación"
        ordering = ['nombre']
    def __str__(self):
        return self.nombre


# --- Modelo Principal de Producto (Con las correcciones aplicadas) ---

class Producto(models.Model):
    # ... (todos tus campos están correctos) ...
    nombre = models.CharField(max_length=200, verbose_name="Nombre del Producto")
    descripcion = models.TextField(blank=True, verbose_name="Descripción Detallada")
    codigo_barras = models.CharField(max_length=100, unique=True, blank=True, null=True, verbose_name="Código de Barras (EAN)")
    principio_activo = models.ForeignKey(PrincipioActivo, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Principio Activo")
    concentracion = models.CharField(max_length=100, blank=True, verbose_name="Concentración (ej. 500mg)")
    forma_farmaceutica = models.ForeignKey(FormaFarmaceutica, on_delete=models.PROTECT, verbose_name="Forma Farmacéutica")
    laboratorio = models.ForeignKey(Laboratorio, on_delete=models.PROTECT, verbose_name="Laboratorio")
    categoria = models.ForeignKey(CategoriaProducto, on_delete=models.PROTECT, verbose_name="Categoría")
    unidad_compra = models.ForeignKey(UnidadPresentacion, on_delete=models.PROTECT, related_name='productos_comprados', verbose_name="Unidad de Compra Principal", help_text="La unidad en la que normalmente se compra este producto (ej. Caja).", null=True, blank=True)
    unidad_venta = models.ForeignKey(UnidadPresentacion, on_delete=models.PROTECT, related_name='productos_vendidos', verbose_name="Unidad de Venta Mínima", help_text="La unidad mínima en la que se vende el producto (ej. Tableta, Unidad).", null=True, blank=True)
    margen_ganancia_sugerido = models.DecimalField(max_digits=5, decimal_places=2, default=0.20, verbose_name="Margen de Ganancia Sugerido (%)", help_text="Ej: 0.20 para 20% de margen.")
    precio_venta_sugerido = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00,
        verbose_name="Precio de Venta Sugerido (Global)"
    )
    unidades_por_caja = models.PositiveIntegerField(
        default=1, verbose_name="Unidades por Caja",
        help_text="Total de unidades básicas (pastillas, cápsulas) que contiene la caja."
    )
    unidades_por_blister = models.PositiveIntegerField(
        default=1, verbose_name="Unidades por Blíster",
        help_text="Número de unidades básicas que contiene un blíster."
    )
    aplica_receta = models.BooleanField(default=False, verbose_name="Requiere Receta Médica")
    es_controlado = models.BooleanField(default=False, verbose_name="Es Producto Controlado")
    imagen_producto = models.ImageField(upload_to='productos/', blank=True, null=True, verbose_name="Imagen del Producto")
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Registro")
    
    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['nombre']
        
    def __str__(self):
        return f"{self.nombre} - {self.concentracion}"
    
    def get_unidades_compra_jerarquia(self):
        """
        Devuelve una lista de diccionarios con todas las unidades de presentación
        disponibles para la compra de este producto, incluyendo la unidad de venta
        mínima y sus contenedores (padres).
        """
        if not self.unidad_venta:
            return []

        unidades = []
        unidad_actual = self.unidad_venta
        factor_acumulado = 1

        # Añadimos la unidad base (la mínima)
        unidades.append({
            'id': unidad_actual.id,
            'nombre': unidad_actual.nombre,
            'factor_conversion_a_base': factor_acumulado
        })

        # Recorremos hacia arriba en la jerarquía (de blíster a caja, por ejemplo)
        while unidad_actual.padre:
            unidad_actual = unidad_actual.padre
            factor_acumulado *= unidad_actual.factor_conversion
            unidades.append({
                'id': unidad_actual.id,
                'nombre': unidad_actual.nombre,
                'factor_conversion_a_base': factor_acumulado
            })
        
        return sorted(unidades, key=lambda x: x['factor_conversion_a_base'], reverse=True)
    
   

class StockProducto(models.Model):
    # Añadimos related_name='stocks'
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='stocks', verbose_name="Producto")
    sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE, verbose_name="Sucursal")
    lote = models.CharField(max_length=50, verbose_name="Número de Lote")
    fecha_vencimiento = models.DateField(verbose_name="Fecha de Vencimiento")
    cantidad = models.PositiveIntegerField(default=0, verbose_name="Cantidad Disponible", help_text="Cantidad del producto en su 'unidad de venta mínima' (ej. número de tabletas).")
    precio_compra = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00,
        verbose_name="Precio de Compra del Lote"
    )
    precio_venta = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00,
        verbose_name="Precio de Venta en esta Sucursal"
    )
    ubicacion_almacen = models.CharField(max_length=100, blank=True, verbose_name="Ubicación en Almacén")
    ultima_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")
    
    class Meta:
        verbose_name = "Stock de Producto"
        verbose_name_plural = "Stocks de Productos"
        unique_together = ('producto', 'sucursal', 'lote')
        ordering = ['sucursal__nombre', 'producto__nombre', 'fecha_vencimiento']
        
    def __str__(self):
        return f"{self.producto.nombre} ({self.lote}) - Suc: {self.sucursal.nombre} - Cant: {self.cantidad}"
    
    
class MovimientoInventario(models.Model):
    TIPO_MOVIMIENTO_CHOICES = [('ENTRADA', 'Entrada'), ('SALIDA', 'Salida'), ('AJUSTE_POSITIVO', 'Ajuste Positivo'), ('AJUSTE_NEGATIVO', 'Ajuste Negativo')]
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, verbose_name="Producto Afectado")
    sucursal = models.ForeignKey(Sucursal, on_delete=models.PROTECT, verbose_name="Sucursal del Movimiento")
    stock_afectado = models.ForeignKey(StockProducto, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Stock de Producto Afectado")
    tipo_movimiento = models.CharField(max_length=50, choices=TIPO_MOVIMIENTO_CHOICES, verbose_name="Tipo de Movimiento")
    cantidad = models.IntegerField(verbose_name="Cantidad del Movimiento (en unidad de venta)")
    fecha_movimiento = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y Hora del Movimiento")
    usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT, verbose_name="Usuario que realizó el movimiento")
    referencia_doc = models.CharField(max_length=100, blank=True, verbose_name="Referencia de Documento")
    observaciones = models.TextField(blank=True, verbose_name="Observaciones Adicionales")
    class Meta:
        verbose_name = "Movimiento de Inventario"
        verbose_name_plural = "Movimientos de Inventario"
        ordering = ['-fecha_movimiento']
    def __str__(self):
        return f"{self.tipo_movimiento} de {self.cantidad} de {self.producto.nombre} en {self.sucursal.nombre}"