from django import forms
from .models import CategoriaProducto

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