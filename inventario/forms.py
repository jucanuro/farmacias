from django import forms
from .models import CategoriaProducto, Laboratorio, FormaFarmaceutica, PrincipioActivo, Producto, Sucursal, MovimientoInventario, UnidadPresentacion

class CategoriaProductoForm(forms.ModelForm):
    class Meta:
        model = CategoriaProducto
        fields = ['nombre', 'descripcion']

        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 mt-1 border border-slate-600 bg-slate-800 text-white placeholder-slate-400 rounded-lg focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-sky-500',
                'placeholder': 'Ej: Analgésicos'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 mt-1 border border-slate-600 bg-slate-800 text-white placeholder-slate-400 rounded-lg focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-sky-500',
                'placeholder': 'Breve descripción de la categoría...',
                'rows': 3
            }),
        }

        labels = {
            'nombre': 'Nombre de la Categoría',
            'descripcion': 'Descripción',
        }
        
        
class LaboratorioForm(forms.ModelForm):
    class Meta:
        model = Laboratorio
        fields = ['nombre', 'direccion', 'telefono', 'email']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'w-full px-3 py-2 mt-1 border border-slate-600 bg-slate-800 text-white placeholder-slate-400 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500', 'placeholder': 'Ej: Bayer'}),
            'direccion': forms.TextInput(attrs={'class': 'w-full px-3 py-2 mt-1 border border-slate-600 bg-slate-800 text-white placeholder-slate-400 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500', 'placeholder': 'Av. Ejemplo 123'}),
            'telefono': forms.TextInput(attrs={'class': 'w-full px-3 py-2 mt-1 border border-slate-600 bg-slate-800 text-white placeholder-slate-400 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500', 'placeholder': '987654321'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-3 py-2 mt-1 border border-slate-600 bg-slate-800 text-white placeholder-slate-400 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500', 'placeholder': 'contacto@laboratorio.com'}),
        }
        labels = {'nombre': 'Nombre del Laboratorio', 'direccion': 'Dirección', 'telefono': 'Teléfono', 'email': 'Email de Contacto'}
        
class FormaFarmaceuticaForm(forms.ModelForm):
    class Meta:
        model = FormaFarmaceutica
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'w-full px-3 py-2 mt-1 border border-slate-600 bg-slate-800 text-white placeholder-slate-400 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500', 'placeholder': 'Ej: Tableta, Jarabe, Crema'}),
            'descripcion': forms.Textarea(attrs={'class': 'w-full px-3 py-2 mt-1 border border-slate-600 bg-slate-800 text-white placeholder-slate-400 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500', 'placeholder': 'Breve descripción de la forma...', 'rows': 3}),
        }
        labels = {'nombre': 'Nombre de la Forma Farmacéutica', 'descripcion': 'Descripción'}
        
class PrincipioActivoForm(forms.ModelForm):
    class Meta:
        model = PrincipioActivo
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'w-full px-3 py-2 mt-1 border border-slate-600 bg-slate-800 text-white placeholder-slate-400 rounded-lg focus:outline-none focus:ring-2 focus:ring-rose-500 focus:border-rose-500', 'placeholder': 'Ej: Paracetamol, Ibuprofeno'}),
            'descripcion': forms.Textarea(attrs={'class': 'w-full px-3 py-2 mt-1 border border-slate-600 bg-slate-800 text-white placeholder-slate-400 rounded-lg focus:outline-none focus:ring-2 focus:ring-rose-500 focus:border-rose-500', 'placeholder': 'Breve descripción del principio activo...', 'rows': 3}),
        }
        labels = {'nombre': 'Nombre del Principio Activo', 'descripcion': 'Descripción'}
        
class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        exclude = ['precio_compra_promedio', 'fecha_registro']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-input'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
            'codigo_barras': forms.TextInput(attrs={'class': 'form-input'}),
            'principio_activo': forms.Select(attrs={'class': 'form-select'}),
            'concentracion': forms.TextInput(attrs={'class': 'form-input'}),
            'forma_farmaceutica': forms.Select(attrs={'class': 'form-select'}),
            'laboratorio': forms.Select(attrs={'class': 'form-select'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'presentacion_base': forms.Select(attrs={'class': 'form-select'}),
            'cantidad_por_presentacion_base': forms.NumberInput(attrs={'class': 'form-input'}),
            'unidad_medida': forms.Select(attrs={'class': 'form-select'}),
            'margen_ganancia_sugerido': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'aplica_receta': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'es_controlado': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'imagen_producto': forms.ClearableFileInput(attrs={'class': 'form-input-file'}),
        }
    
    
class StockEntradaForm(forms.Form):
    sucursal = forms.ModelChoiceField(
        queryset=Sucursal.objects.all().order_by('nombre'),
        label="Sucursal de Destino",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    lote = forms.CharField(
        max_length=50,
        label="Número de Lote",
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ej: XJ500-A1'})
    )
    fecha_vencimiento = forms.DateField(
        label="Fecha de Vencimiento",
        widget=forms.DateInput(attrs={'class': 'form-input', 'type': 'date'})
    )
    cantidad = forms.IntegerField(
        min_value=1,
        label="Cantidad Recibida",
        help_text="Cantidad en la 'presentación base' del producto (ej. número de cajas).",
        widget=forms.NumberInput(attrs={'class': 'form-input'})
    )
    precio_compra_lote = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0.01,
        label="Precio de Compra del Lote",
        help_text="Precio por cada 'presentación base' en esta compra.",
        widget=forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'})
    )
    ubicacion_almacen = forms.CharField(
        max_length=100,
        required=False,
        label="Ubicación en Almacén (Opcional)",
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ej: Estante A-3'})
    )
    
class UnidadPresentacionForm(forms.ModelForm):
    class Meta:
        model = UnidadPresentacion
        fields = ['nombre', 'padre', 'factor_conversion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-input'}),
            'padre': forms.Select(attrs={'class': 'form-select'}),
            'factor_conversion': forms.NumberInput(attrs={'class': 'form-input'}),
        }