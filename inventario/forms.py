from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column
from .models import CategoriaProducto, Laboratorio, FormaFarmaceutica, PrincipioActivo, Producto, Sucursal, MovimientoInventario, UnidadPresentacion,StockProducto

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
    def __init__(self, *args, **kwargs):
        print(">>> ¡El código nuevo de ProductoForm se está ejecutando! <<<")
        super().__init__(*args, **kwargs)
        
        # --- 2. Crea y configura el FormHelper ---
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        # Quita el <form> tag de crispy, ya que lo tenemos en el HTML
        self.helper.form_tag = False 
        
        # --- 3. Define la estructura de 3 columnas ---
        self.helper.layout = Layout(
            # Añadimos clases de grid y gap a cada Fila (Row)
            Row(
                Column('nombre'),
                Column('categoria'),
                Column('laboratorio'),
                # grid-cols-3: Crea 3 columnas
                # gap-6: Añade un espacio generoso entre ellas
                # mb-4: Añade un margen inferior para separar las filas
                css_class='grid md:grid-cols-3 gap-6 mb-4'
            ),
            Row(
                Column('principio_activo'),
                Column('concentracion'),
                Column('forma_farmaceutica'),
                css_class='grid md:grid-cols-3 gap-6 mb-4'
            ),
            Row(
                Column('unidad_compra'),
                Column('unidad_venta'),
                Column('unidades_por_caja'),
                css_class='grid md:grid-cols-3 gap-6 mb-4'
            ),
            Row(
                Column('unidades_por_blister'),
                Column('margen_ganancia_sugerido'),
                Column('precio_venta_sugerido'),
                css_class='grid md:grid-cols-3 gap-6 mb-4'
            ),
            Row(
                 Column('codigo_barras'),
                 # Dejamos las otras 2 columnas vacías para que ocupe 1/3 del espacio
                 Column(),
                 Column(),
                 css_class='grid md:grid-cols-3 gap-6 mb-4'
            ),
            'descripcion',
            Row(
                Column('aplica_receta'),
                Column('es_controlado'),
                css_class='flex gap-x-8 mb-4' # Usamos flexbox para los checkboxes
            ),
            'imagen_producto'
        )
        
        if not self.instance.pk:
            self.fields['margen_ganancia_sugerido'].initial = 0.20
            self.fields['unidades_por_caja'].initial = 1
            self.fields['unidades_por_blister'].initial = 1
            
            # Opcional pero recomendado: poner un valor inicial para el precio sugerido
            self.fields['precio_venta_sugerido'].initial = 0.00
    class Meta:
        model = Producto
        # Usamos 'fields' para listar explícitamente los campos que queremos.
        # Quitamos los precios específicos y dejamos solo el sugerido.
        fields = '__all__'
        
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'bg-slate-800 text-black border border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 p-2 rounded-md placeholder-gray-400'}),
            'descripcion': forms.Textarea(attrs={'class': 'bg-slate-800 text-black border border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 p-2 rounded-md h-24 placeholder-gray-400'}),
            'codigo_barras': forms.TextInput(attrs={'class': 'bg-slate-800 text-black border border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 p-2 rounded-md placeholder-gray-400'}),
            'principio_activo': forms.Select(attrs={'class': 'bg-slate-800 text-black border border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 p-2 rounded-md appearance-none pr-8'}), # Eliminamos 'custom-select-arrow-white' si no usas CSS custom
            'concentracion': forms.TextInput(attrs={'class': 'bg-slate-800 text-black border border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 p-2 rounded-md placeholder-gray-400'}),
            'forma_farmaceutica': forms.Select(attrs={'class': 'bg-slate-800 text-black border border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 p-2 rounded-md appearance-none pr-8'}),
            'laboratorio': forms.Select(attrs={'class': 'bg-slate-800 text-black border border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 p-2 rounded-md appearance-none pr-8'}),
            'categoria': forms.Select(attrs={'class': 'bg-slate-800 text-black border border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 p-2 rounded-md appearance-none pr-8'}),
            'unidad_compra': forms.Select(attrs={'class': 'bg-slate-800 text-black border border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 p-2 rounded-md appearance-none pr-8'}),
            'unidad_venta': forms.Select(attrs={'class': 'bg-slate-800 text-black border border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 p-2 rounded-md appearance-none pr-8'}),
            'margen_ganancia_sugerido': forms.NumberInput(attrs={'class': 'bg-slate-800 text-black border border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 p-2 rounded-md placeholder-gray-400', 'step': '0.01'}),
            'precio_venta_sugerido': forms.NumberInput(attrs={'class': 'bg-slate-800 text-black border border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 p-2 rounded-md placeholder-gray-400', 'step': '0.01'}),
            'unidades_por_caja': forms.NumberInput(attrs={'class': 'bg-slate-800 text-black border border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 p-2 rounded-md placeholder-gray-400'}),
            'unidades_por_blister': forms.NumberInput(attrs={'class': 'bg-slate-800 text-black border border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 p-2 rounded-md placeholder-gray-400'}),
            'aplica_receta': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-blue-600 bg-slate-800 border-gray-700 rounded focus:ring-blue-500'}),
            'es_controlado': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-black bg-slate-800 border-gray-700 rounded focus:ring-blue-500'}),
            'imagen_producto': forms.ClearableFileInput(attrs={'class': 'bg-slate-800 text-black border border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 p-2 rounded-md placeholder-gray-400'}),
        }
    
    
class StockEntradaForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        # Usaremos el <form> de nuestra plantilla, no el de crispy
        self.helper.form_tag = False
        self.helper.layout = Layout(
            'sucursal',
            # Usamos una rejilla para organizar los campos
            Row(
                Column('lote', css_class='w-full md:w-1/2'),
                Column('fecha_vencimiento', css_class='w-full md:w-1/2'),
                css_class='grid md:grid-cols-2 gap-4 mt-4'
            ),
            Row(
                Column('cantidad', css_class='w-full md:w-1/2'),
                Column('precio_compra', css_class='w-full md:w-1/2'),
                css_class='grid md:grid-cols-2 gap-4 mt-4'
            ),
            Row(
                # El precio de venta ocupa todo el ancho de su fila
                Column('precio_venta', css_class='w-full'),
                css_class='mt-4'
            ),
             Row(
                Column('ubicacion_almacen', css_class='w-full'),
                css_class='mt-4'
            )
        )

    class Meta:
        model = StockProducto
        fields = [
            'sucursal', 
            'lote', 
            'fecha_vencimiento', 
            'cantidad', 
            'precio_compra', 
            'precio_venta',
            'ubicacion_almacen'
        ]
        
        widgets = {
            'sucursal': forms.Select(attrs={'class': 'form-select'}),
            'lote': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ej: XJ500-A1'}),
            'fecha_vencimiento': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-input'}),
            'precio_compra': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'ubicacion_almacen': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ej: Estante A-3'}),
        }
        
        labels = {
            'cantidad': 'Cantidad Recibida (en unidades mínimas)',
            'precio_compra': 'Precio de Compra (por unidad mínima)',
            'precio_venta': 'Precio de Venta para este Lote',
        }
    
class UnidadPresentacionForm(forms.ModelForm):
    class Meta:
        model = UnidadPresentacion
        fields = ['nombre', 'padre', 'factor_conversion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-input'}),
            'padre': forms.Select(attrs={'class': 'form-select'}),
            'factor_conversion': forms.NumberInput(attrs={'class': 'form-input'}),
        }