import json
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login, logout
from rest_framework.authtoken.models import Token
from .forms import (
    CustomUserCreationForm, 
    FarmaciaForm, 
    SucursalForm, 
    RolForm, 
    UsuarioCreateForm, 
    UsuarioUpdateForm
)
from .models import Farmacia, Sucursal, Rol, Usuario

def home_view(request):
    return HttpResponse("<h1>¡Bienvenido al Sistema de Gestión de Farmacias!</h1><p>Esta es la página de inicio de la aplicación core.</p>")

@require_POST
def registro_api_view(request):
    try:
        data = json.loads(request.body)
        form = CustomUserCreationForm(data)
        if form.is_valid():
            user = form.save()
            login(request, user)
            dashboard_url = reverse('dashboard') 
            return JsonResponse({'status': 'success', 'message': '¡Registro exitoso!', 'redirect_url': dashboard_url})
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Error inesperado: {str(e)}'}, status=500)

@require_POST
def login_api_view(request):
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            dashboard_url = reverse('dashboard')
            return JsonResponse({'status': 'success', 'message': '¡Inicio de sesión exitoso!', 'token': token.key, 'redirect_url': dashboard_url})
        else:
            return JsonResponse({'status': 'error', 'message': 'Usuario o contraseña inválidos.'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Error inesperado: {str(e)}'}, status=500)

def logout_view(request):
    logout(request)
    return redirect('login')

def farmacias_list_view(request):
    lista_de_farmacias = Farmacia.objects.all().order_by('nombre')
    context = {'farmacias': lista_de_farmacias}
    return render(request, 'farmacias_main_templates/farmacias_list.html', context)

def farmacia_create_view(request):
    if request.method == 'POST':
        form = FarmaciaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('core:farmacias_list')
    else:
        form = FarmaciaForm()
    context = {'form': form}
    return render(request, 'farmacias_main_templates/farmacia_form.html', context)

def farmacia_update_view(request, pk):
    farmacia_a_editar = get_object_or_404(Farmacia, pk=pk)
    if request.method == 'POST':
        form = FarmaciaForm(request.POST, request.FILES, instance=farmacia_a_editar)
        if form.is_valid():
            form.save()
            return redirect('core:farmacias_list')
    else:
        form = FarmaciaForm(instance=farmacia_a_editar)
    context = {'form': form, 'farmacia': farmacia_a_editar}
    return render(request, 'farmacias_main_templates/farmacia_form.html', context)

@require_POST
def farmacia_delete_view(request, pk):
    farmacia_a_eliminar = get_object_or_404(Farmacia, pk=pk)
    farmacia_a_eliminar.delete()
    return redirect('core:farmacias_list')

def sucursal_list_view(request, farmacia_id):
    farmacia = get_object_or_404(Farmacia, pk=farmacia_id)
    lista_de_sucursales = farmacia.sucursales.all().order_by('nombre')
    context = {'farmacia': farmacia, 'sucursales': lista_de_sucursales}
    return render(request, 'farmacias_main_templates/sucursal_list.html', context)

def sucursal_create_view(request, farmacia_id):
    farmacia = get_object_or_404(Farmacia, pk=farmacia_id)
    if request.method == 'POST':
        form = SucursalForm(request.POST, farmacia_id=farmacia.pk)
        if form.is_valid():
            sucursal = form.save(commit=False)
            sucursal.farmacia = farmacia
            sucursal.save()
            return redirect('core:sucursal_list', farmacia_id=farmacia.pk)
    else:
        form = SucursalForm(farmacia_id=farmacia.pk)
    context = {'form': form, 'farmacia': farmacia}
    return render(request, 'farmacias_main_templates/sucursal_form.html', context)

def sucursal_update_view(request, pk):
    sucursal = get_object_or_404(Sucursal, pk=pk)
    farmacia = sucursal.farmacia
    if request.method == 'POST':
        form = SucursalForm(request.POST, instance=sucursal, farmacia_id=farmacia.pk)
        if form.is_valid():
            form.save()
            return redirect('core:sucursal_list', farmacia_id=farmacia.pk)
    else:
        form = SucursalForm(instance=sucursal, farmacia_id=farmacia.pk)
    context = {'form': form, 'farmacia': farmacia, 'sucursal': sucursal}
    return render(request, 'farmacias_main_templates/sucursal_form.html', context)

@require_POST
def sucursal_delete_view(request, pk):
    sucursal_a_eliminar = get_object_or_404(Sucursal, pk=pk)
    farmacia_id = sucursal_a_eliminar.farmacia.pk
    sucursal_a_eliminar.delete()
    return redirect('core:sucursal_list', farmacia_id=farmacia_id)

def rol_list_view(request):
    lista_de_roles = Rol.objects.all().order_by('nombre')
    context = {'roles': lista_de_roles}
    return render(request, 'roles_templates/rol_list.html', context)

def rol_create_view(request):
    if request.method == 'POST':
        form = RolForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('core:rol_list')
    else:
        form = RolForm()
    context = {'form': form}
    return render(request, 'roles_templates/rol_form.html', context)

def rol_update_view(request, pk):
    rol = get_object_or_404(Rol, pk=pk)
    if request.method == 'POST':
        form = RolForm(request.POST, instance=rol)
        if form.is_valid():
            form.save()
            return redirect('core:rol_list')
    else:
        form = RolForm(instance=rol)
    context = {'form': form, 'rol': rol}
    return render(request, 'roles_templates/rol_form.html', context)

@require_POST
def rol_delete_view(request, pk):
    rol_a_eliminar = get_object_or_404(Rol, pk=pk)
    rol_a_eliminar.delete()
    return redirect('core:rol_list')

def usuario_list_view(request):
    lista_de_usuarios = Usuario.objects.all().select_related(
        'farmacia', 'sucursal', 'rol'
    ).order_by('username')
    context = {'usuarios': lista_de_usuarios}
    return render(request, 'usuarios_templates/usuario_list.html', context)

def usuario_create_view(request):
    if request.method == 'POST':
        form = UsuarioCreateForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('core:usuario_list')
    else:
        form = UsuarioCreateForm()
    context = {'form': form}
    return render(request, 'usuarios_templates/usuario_form.html', context)

def usuario_update_view(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    if request.method == 'POST':
        form = UsuarioUpdateForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            return redirect('core:usuario_list')
    else:
        form = UsuarioUpdateForm(instance=usuario)
    context = {'form': form, 'usuario': usuario}
    return render(request, 'usuarios_templates/usuario_form.html', context)

@require_POST
def usuario_toggle_active_view(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    if not usuario.is_superuser:
        usuario.is_active = not usuario.is_active
        usuario.save()
        return JsonResponse({'status': 'success', 'is_active': usuario.is_active})
    return JsonResponse({'status': 'error', 'message': 'No se puede cambiar el estado de un superusuario.'}, status=403)