from django import forms
from .models import Proveedor

class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        # Excluimos 'fecha_registro' porque se genera automáticamente
        exclude = ['fecha_registro']
        # Definimos los widgets para aplicar los estilos de la plantilla
        widgets = {
            'nombre_comercial': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ej: Distribuidora Farma SAC'}),
            'razon_social': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ej: Distribuidora Farmacéutica VQL S.A.C.'}),
            'tipo_documento': forms.Select(attrs={'class': 'form-select'}),
            'numero_documento': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ej: 20123456789'}),
            'direccion': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Av. La Peruanidad 123, Huaraz'}),
            'telefono': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '987654321'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'ventas@proveedor.com'}),
            'sitio_web': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'https://www.proveedor.com'}),
            'persona_contacto': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Nombre del vendedor o contacto'}),
            'telefono_contacto': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Celular del contacto'}),
            'condiciones_pago': forms.Textarea(attrs={'class': 'form-input', 'rows': 2, 'placeholder': 'Ej: Crédito a 30 días'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }