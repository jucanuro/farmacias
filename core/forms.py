from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.db.models import Q
from .models import Usuario, Farmacia, Sucursal, Rol


class FarmaciaForm(forms.ModelForm):
    class Meta:
        model = Farmacia
        fields = ['nombre', 'razon_social', 'ruc', 'direccion', 'telefono', 'email', 'logo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'w-full px-3 py-2 mt-1 border border-slate-600 bg-slate-800 text-white placeholder-slate-400 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500', 'placeholder': 'Ej: Farmacia VQL Central'}),
            'razon_social': forms.TextInput(attrs={'class': 'w-full px-3 py-2 mt-1 border border-slate-600 bg-slate-800 text-white placeholder-slate-400 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500', 'placeholder': 'Ej: VQL S.A.C.'}),
            'ruc': forms.TextInput(attrs={'class': 'w-full px-3 py-2 mt-1 border border-slate-600 bg-slate-800 text-white placeholder-slate-400 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500', 'placeholder': 'Ej: 20123456789'}),
            'direccion': forms.TextInput(attrs={'class': 'w-full px-3 py-2 mt-1 border border-slate-600 bg-slate-800 text-white placeholder-slate-400 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500', 'placeholder': 'Ej: Av. Principal 123'}),
            'telefono': forms.TextInput(attrs={'class': 'w-full px-3 py-2 mt-1 border border-slate-600 bg-slate-800 text-white placeholder-slate-400 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500', 'placeholder': 'Ej: 987654321'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-3 py-2 mt-1 border border-slate-600 bg-slate-800 text-white placeholder-slate-400 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500', 'placeholder': 'ejemplo@farmacia.com'}),
            'logo': forms.ClearableFileInput(attrs={'class': 'w-full text-sm text-slate-400 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-emerald-500/10 file:text-emerald-400 hover:file:bg-emerald-500/20'})
        }

class SucursalForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        farmacia_id = kwargs.pop('farmacia_id', None)
        super().__init__(*args, **kwargs)

        if not (farmacia_id or (self.instance and self.instance.pk)):
            self.fields['administrador'].queryset = Usuario.objects.none()
            return

        farmacia = self.instance.farmacia if self.instance and self.instance.pk else Farmacia.objects.get(pk=farmacia_id)
        
        roles_administrativos = ['Administrador de Farmacia', 'Gerente de Sucursal']
        
        condicion_rol = Q(farmacia=farmacia) & Q(rol__nombre__in=roles_administrativos)
        
        condicion_superuser = Q(is_superuser=True)
        
        self.fields['administrador'].queryset = Usuario.objects.filter(
            condicion_rol | condicion_superuser
        ).distinct()

    class Meta:
        model = Sucursal
        fields = ['nombre', 'codigo', 'direccion', 'telefono', 'administrador', 'fecha_apertura']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'w-full px-3 py-2 mt-1 border border-slate-600 bg-slate-800 text-white placeholder-slate-400 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500', 'placeholder': 'Ej: Sucursal Centro'}),
            'codigo': forms.TextInput(attrs={'class': 'w-full px-3 py-2 mt-1 border border-slate-600 bg-slate-800 text-white placeholder-slate-400 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500', 'placeholder': 'Ej: CEN01'}),
            'direccion': forms.TextInput(attrs={'class': 'w-full px-3 py-2 mt-1 border border-slate-600 bg-slate-800 text-white placeholder-slate-400 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500', 'placeholder': 'Ej: Jr. San Martín 456'}),
            'telefono': forms.TextInput(attrs={'class': 'w-full px-3 py-2 mt-1 border border-slate-600 bg-slate-800 text-white placeholder-slate-400 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500', 'placeholder': 'Ej: 912345678'}),
            'administrador': forms.Select(attrs={'class': 'w-full px-3 py-2 mt-1 border border-slate-600 bg-slate-800 text-white placeholder-slate-400 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500'}),
            'fecha_apertura': forms.DateInput(attrs={'class': 'w-full px-3 py-2 mt-1 border border-slate-600 bg-slate-800 text-white placeholder-slate-400 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500', 'type': 'date'}),
        }
        
class RolForm(forms.ModelForm):
 
    class Meta:
        model = Rol
        fields = ['nombre', 'descripcion']

        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 mt-1 border border-slate-600 bg-slate-800 text-white placeholder-slate-400 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': 'Ej: Administrador de Farmacia'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 mt-1 border border-slate-600 bg-slate-800 text-white placeholder-slate-400 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': 'Describe brevemente las responsabilidades de este rol...',
                'rows': 3
            }),
        }

        labels = {
            'nombre': 'Nombre del Rol',
            'descripcion': 'Descripción',
        }
        
        
class UsuarioCreateForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = (
            "username", 
            "first_name", 
            "last_name", 
            "email", 
            "farmacia", 
            "sucursal", 
            "rol",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({
                'class': 'w-full px-3 py-2 mt-1 border border-slate-600 bg-slate-800 text-white placeholder-slate-400 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500'
            })

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = ("username", "email", "farmacia", "rol")
        
        
        
class UsuarioUpdateForm(UserChangeForm):
    # Hacemos que el campo de contraseña no sea requerido, de hecho, lo ocultaremos en la plantilla
    password = None

    class Meta:
        model = Usuario
        # Campos que se podrán editar. Excluimos 'username' para evitar cambiar el login.
        fields = (
            "first_name", 
            "last_name", 
            "email", 
            "farmacia", 
            "sucursal", 
            "rol",
            "is_active", # Permitimos cambiar el estado desde el formulario de edición
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Aplicamos los estilos de Tailwind a todos los campos
        for field_name in self.fields:
            if self.fields[field_name]:
                self.fields[field_name].widget.attrs.update({
                    'class': 'w-full px-3 py-2 mt-1 border border-slate-600 bg-slate-800 text-white placeholder-slate-400 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500'
                })