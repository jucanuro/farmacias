import json
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login, logout
from rest_framework.authtoken.models import Token
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.db import IntegrityError

from django.contrib.auth.decorators import login_required, user_passes_test

from .models import Farmacia, Sucursal, Rol, Usuario, ConfiguracionFacturacionElectronica, SerieComprobante


def enviar_factura_service(invoice_data, configuracion):
    if invoice_data and configuracion:
        return {'success': True, 'invoice_id': 'INV-12345'}
    return {'success': False, 'error': 'Datos de factura o configuración faltantes'}


def home_view(request):
    return render(request, 'landing.html')


@require_POST
def registro_view(request):
    if request.user.is_authenticated and request.user.farmacia:
        return redirect('dashboard') 

    if request.method == 'POST':
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        errores = []

        if not username:
            errores.append("El nombre de usuario es obligatorio.")
        elif Usuario.objects.filter(username=username).exists():
            errores.append("El nombre de usuario ya está registrado.")

        if password1 != password2:
            errores.append("Las contraseñas no coinciden.")

        try:
            validate_password(password1)
        except ValidationError as e:
            errores.extend(e.messages)

        if errores:
            context = {
                "errores": errores,
                "username": username,
                "email": email,
            }
            return render(request, 'registration/registro.html', context)

        try:
            user = Usuario.objects.create_user(
                username=username,
                email=email,
                password=password1
            )
            
            login(request, user)

            return redirect('core:farmacia_create')

        except Exception as e:
            context = {
                "errores": [f"Error inesperado al crear la cuenta: {str(e)}"],
                "username": username,
                "email": email,
            }
            return render(request, 'registration/registro.html', context)

    return render(request, 'registration/registro.html')


@require_POST
def login_view(request):
    if request.user.is_authenticated:
        if hasattr(request.user, 'farmacia') and request.user.farmacia:
            return redirect('core:dashboard') 
        return redirect('core:farmacia_create')

    if request.method == 'POST':
        action_type = request.POST.get('action_type')

        if action_type == 'login':
            username = request.POST.get('username', '').strip()
            password = request.POST.get('password', '')

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if hasattr(user, 'farmacia') and user.farmacia:
                    return redirect('core:dashboard')  
                return redirect('core:farmacia_create')   
            else:
                return render(request, 'farmacias_main_templates/index.html', {
                    'error_login': 'Usuario o contraseña incorrectos.',
                    'login_username': username
                })

        elif action_type == 'register':
            reg_username = request.POST.get('reg_username', '').strip()
            reg_email = request.POST.get('reg_email', '').strip()
            reg_password1 = request.POST.get('reg_password1')
            reg_password2 = request.POST.get('reg_password2')

            errores = []

            if not reg_username:
                errores.append("El nombre de usuario es obligatorio.")
            elif Usuario.objects.filter(username=reg_username).exists():
                errores.append("El nombre de usuario ya está registrado.")

            if reg_password1 != reg_password2:
                errores.append("Las contraseñas no coinciden.")

            try:
                validate_password(reg_password1)
            except ValidationError as e:
                errores.extend(e.messages)

            if errores:
                return render(request, 'farmacias_main_templates/index.html', {
                    'errores_registro': errores,
                    'reg_username': reg_username,
                    'reg_email': reg_email
                })

            try:
                Usuario.objects.create_user(
                    username=reg_username,
                    email=reg_email,
                    password=reg_password1
                )
                return render(request, 'farmacias_main_templates/index.html', {
                    'success_register': '¡Cuenta creada con éxito! Ya puedes acceder al sistema.',
                    'login_username': reg_username
                })
            except Exception as e:
                return render(request, 'farmacias_main_templates/index.html', {
                    'errores_registro': [f"Error al crear la cuenta: {str(e)}"],
                    'reg_username': reg_username,
                    'reg_email': reg_email
                })

    return render(request, 'farmacias_main_templates/index.html')

def logout_view(request):
    logout(request)
    return redirect('login')


def farmacias_list_view(request):
    lista_de_farmacias = Farmacia.objects.all().order_by('nombre')
    context = {'farmacias': lista_de_farmacias}
    return render(request, 'farmacias_main_templates/farmacias_list.html', context)

def farmacia_create_view(request):
    if hasattr(request.user, 'farmacia') and request.user.farmacia:
        return redirect('core:dashboard')

    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        ruc = request.POST.get('ruc', '').strip()
        direccion = request.POST.get('direccion', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        logo = request.FILES.get('logo')

        errores = []

        if not nombre:
            errores.append("El nombre de la farmacia es obligatorio.")
        if not ruc or len(ruc) != 11:
            errores.append("El RUC debe tener exactamente 11 dígitos.")
        
        if errores:
            return render(request, 'farmacias_main_templates/farmacia_form.html', {
                'errores': errores,
                'datos': request.POST
            })

        try:
            nueva_farmacia = Farmacia.objects.create(
                nombre=nombre,
                ruc=ruc,
                direccion=direccion,
                telefono=telefono,
                logo=logo
            )

            request.user.farmacia = nueva_farmacia
            request.user.save()

            return redirect('core:dashboard')

        except Exception as e:
            return render(request, 'farmacias_main_templates/farmacia_form.html', {
                'errores': [f"Error al registrar la farmacia: {str(e)}"],
                'datos': request.POST
            })

    return render(request, 'farmacias_main_templates/farmacia_form.html')

@require_POST
def farmacia_update_view(request, pk):
    farmacia_a_editar = get_object_or_404(Farmacia, pk=pk)

    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        ruc = request.POST.get('ruc', '').strip()
        direccion = request.POST.get('direccion', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        logo = request.FILES.get('logo')

        errores = []

        if not nombre:
            errores.append("El nombre de la farmacia es obligatorio.")
        if not ruc or len(ruc) != 11:
            errores.append("El RUC debe tener exactamente 11 dígitos.")

        if errores:
            return render(request, 'farmacias_main_templates/farmacia_form.html', {
                'errores': errores,
                'farmacia': farmacia_a_editar  
            })

        try:
            farmacia_a_editar.nombre = nombre
            farmacia_a_editar.ruc = ruc
            farmacia_a_editar.direccion = direccion
            farmacia_a_editar.telefono = telefono
            
            if logo:
                farmacia_a_editar.logo = logo

            farmacia_a_editar.save()
            return redirect('core:farmacias_list')

        except Exception as e:
            return render(request, 'farmacias_main_templates/farmacia_form.html', {
                'errores': [f"Error al actualizar los datos: {str(e)}"],
                'farmacia': farmacia_a_editar
            })

    return render(request, 'farmacias_main_templates/farmacia_form.html', {
        'farmacia': farmacia_a_editar
    })

def farmacia_delete_view(request, pk):
    farmacia = get_object_or_404(Farmacia, pk=pk)
    
    if request.method == 'POST':
        try:
            farmacia.delete()
            return redirect('core:farmacias_list')
        except Exception as e:
            return render(request, 'farmacias_main_templates/farmacias_list.html', {
                'error_eliminacion': f"No se pudo eliminar la farmacia: {str(e)}"
            })
            
  
    return render(request, 'farmacias_main_templates/farmacia_confirm_delete.html', {
        'farmacia': farmacia
    })

def sucursal_list_view(request, farmacia_id):
    farmacia = get_object_or_404(Farmacia, pk=farmacia_id)
    lista_de_sucursales = farmacia.sucursales.all().order_by('nombre')
    context = {'farmacia': farmacia, 'sucursales': lista_de_sucursales}
    return render(request, 'farmacias_main_templates/sucursal_list.html', context)

def sucursal_create_view(request, farmacia_id):
    farmacia = get_object_or_404(Farmacia, pk=farmacia_id)
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        direccion = request.POST.get('direccion', '').strip()
        telefono = request.POST.get('telefono', '').strip()

        errores = []

        if not nombre:
            errores.append("El nombre de la sucursal es obligatorio.")
        if not direccion:
            errores.append("La dirección de la sucursal es obligatoria.")

        if errores:
            return render(request, 'farmacias_main_templates/sucursal_form.html', {
                'errores': errores,
                'farmacia': farmacia,
                'datos': request.POST
            })

        try:
            Sucursal.objects.create(
                farmacia=farmacia,
                nombre=nombre,
                direccion=direccion,
                telefono=telefono
            )
            return redirect('core:sucursal_list', farmacia_id=farmacia.pk)

        except Exception as e:
            return render(request, 'farmacias_main_templates/sucursal_form.html', {
                'errores': [f"Error al registrar la sucursal: {str(e)}"],
                'farmacia': farmacia,
                'datos': request.POST
            })

    return render(request, 'farmacias_main_templates/sucursal_form.html', {'farmacia': farmacia})

def sucursal_update_view(request, pk):
    sucursal = get_object_or_404(Sucursal, pk=pk)
    farmacia = sucursal.farmacia

    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        direccion = request.POST.get('direccion', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        es_principal = request.POST.get('es_principal') == 'on' or request.POST.get('es_principal') == 'true'

        errores = []

        if not nombre:
            errores.append("El nombre de la sucursal es obligatorio.")
        if not direccion:
            errores.append("La dirección de la sucursal es obligatoria.")

        if errores:
            return render(request, 'farmacias_main_templates/sucursal_form.html', {
                'errores': errores,
                'farmacia': farmacia,
                'sucursal': sucursal
            })

        try:
            if es_principal:
                Sucursal.objects.filter(farmacia=farmacia, es_principal=True).exclude(pk=pk).update(es_principal=False)

            sucursal.nombre = nombre
            sucursal.direccion = direccion
            sucursal.telefono = telefono
            sucursal.es_principal = es_principal
            sucursal.save()

            return redirect('core:sucursal_list', farmacia_id=farmacia.pk)

        except Exception as e:
            return render(request, 'farmacias_main_templates/sucursal_form.html', {
                'errores': [f"Error al actualizar la sucursal: {str(e)}"],
                'farmacia': farmacia,
                'sucursal': sucursal
            })

    return render(request, 'farmacias_main_templates/sucursal_form.html', {
        'farmacia': farmacia,
        'sucursal': sucursal
    })

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


@login_required
def configuracion_facturacion_view(request):
    if not request.user.farmacia:
        return HttpResponse("No tienes una farmacia asociada para configurar.", status=403)

    farmacia = request.user.farmacia

    try:
        configuracion_fe = farmacia.configuracion_facturacion_electronica
    except ConfiguracionFacturacionElectronica.DoesNotExist:
        configuracion_fe = ConfiguracionFacturacionElectronica.objects.create()
        farmacia.configuracion_facturacion_electronica = configuracion_fe
        farmacia.save()

    if request.method == 'POST':
        form = ConfiguracionFacturacionForm(request.POST, instance=configuracion_fe)
        if form.is_valid():
            form.save()
            return redirect('core:configuracion_facturacion')
    else:
        form = ConfiguracionFacturacionForm(instance=configuracion_fe)

    context = {
        'farmacia': farmacia,
        'form': form,
    }
    return render(request, 'core/configuracion_facturacion.html', context)


@login_required
@require_POST
def enviar_factura_electronica_view(request):
    if not request.user.farmacia:
        return JsonResponse({'status': 'error', 'message': 'El usuario no tiene una farmacia asociada.'}, status=403)

    try:
        data = json.loads(request.body)
        invoice_data = data.get('invoice')

        if not invoice_data:
            return JsonResponse({'status': 'error', 'message': 'Datos de factura no proporcionados.'}, status=400)

        farmacia = request.user.farmacia
        try:
            configuracion_fe = farmacia.configuracion_facturacion_electronica
        except ConfiguracionFacturacionElectronica.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'La configuración de facturación electrónica para la farmacia no existe.'}, status=404)

        response = enviar_factura_service(invoice_data, configuracion_fe)

        if response['success']:
            return JsonResponse({'status': 'success', 'message': 'Factura enviada exitosamente.', 'invoice_id': response['invoice_id']})
        else:
            return JsonResponse({'status': 'error', 'message': response['error']}, status=500)

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Formato JSON inválido.'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Error inesperado: {str(e)}'}, status=500)
    
    
@login_required
def series_list_view(request, farmacia_id):
    farmacia = get_object_or_404(Farmacia, pk=farmacia_id)

    series = SerieComprobante.objects.select_related(
        "farmacia",
        "sucursal"
    ).filter(
        farmacia=farmacia
    ).order_by("sucursal__nombre", "tipo_comprobante", "serie")

    context = {
        "farmacia": farmacia,
        "series": series,
    }

    return render(request, "farmacias_main_templates/series_list.html", context)


@login_required
def serie_create_view(request, farmacia_id):
    farmacia = get_object_or_404(Farmacia, pk=farmacia_id)
    sucursales = farmacia.sucursales.all().order_by("nombre")

    if request.method == "POST":
        sucursal_id = request.POST.get("sucursal")
        tipo_comprobante = request.POST.get("tipo_comprobante")
        serie = (request.POST.get("serie") or "").strip().upper()
        correlativo_actual = request.POST.get("correlativo_actual") or 0
        ambiente = request.POST.get("ambiente") or "BETA"
        activo = request.POST.get("activo") == "on"

        errores = []

        if not sucursal_id:
            errores.append("Debes seleccionar una sucursal.")

        if not tipo_comprobante:
            errores.append("Debes seleccionar el tipo de comprobante.")

        if not serie:
            errores.append("Debes ingresar la serie.")

        if tipo_comprobante == "01" and not serie.startswith("F"):
            errores.append("La serie de factura debe iniciar con F. Ejemplo: F001.")

        if tipo_comprobante == "03" and not serie.startswith("B"):
            errores.append("La serie de boleta debe iniciar con B. Ejemplo: B001.")

        try:
            correlativo_actual = int(correlativo_actual)
            if correlativo_actual < 0:
                errores.append("El correlativo actual no puede ser negativo.")
        except ValueError:
            errores.append("El correlativo actual debe ser un número válido.")

        sucursal = None
        if sucursal_id:
            sucursal = Sucursal.objects.filter(id=sucursal_id, farmacia=farmacia).first()
            if not sucursal:
                errores.append("La sucursal seleccionada no pertenece a esta farmacia.")

        if not errores:
            existe = SerieComprobante.objects.filter(
                farmacia=farmacia,
                sucursal=sucursal,
                tipo_comprobante=tipo_comprobante,
                serie=serie,
                ambiente=ambiente,
            ).exists()

            if existe:
                errores.append("Ya existe una serie igual para esta sucursal, tipo y ambiente.")

        if errores:
            context = {
                "farmacia": farmacia,
                "sucursales": sucursales,
                "errores": errores,
                "serie_data": request.POST,
                "modo": "crear",
            }
            return render(request, "farmacias_main_templates/series_form.html", context)

        SerieComprobante.objects.create(
            farmacia=farmacia,
            sucursal=sucursal,
            tipo_comprobante=tipo_comprobante,
            serie=serie,
            correlativo_actual=correlativo_actual,
            ambiente=ambiente,
            activo=activo,
        )

        return redirect("core:series_list", farmacia_id=farmacia.id)

    context = {
        "farmacia": farmacia,
        "sucursales": sucursales,
        "modo": "crear",
    }

    return render(request, "farmacias_main_templates/series_form.html", context)


@login_required
def serie_update_view(request, pk):
    serie_obj = get_object_or_404(
        SerieComprobante.objects.select_related("farmacia", "sucursal"),
        pk=pk
    )

    farmacia = serie_obj.farmacia
    sucursales = farmacia.sucursales.all().order_by("nombre")

    if request.method == "POST":
        sucursal_id = request.POST.get("sucursal")
        tipo_comprobante = request.POST.get("tipo_comprobante")
        serie = (request.POST.get("serie") or "").strip().upper()
        correlativo_actual = request.POST.get("correlativo_actual") or 0
        ambiente = request.POST.get("ambiente") or "BETA"
        activo = request.POST.get("activo") == "on"

        errores = []

        if not sucursal_id:
            errores.append("Debes seleccionar una sucursal.")

        if not tipo_comprobante:
            errores.append("Debes seleccionar el tipo de comprobante.")

        if not serie:
            errores.append("Debes ingresar la serie.")

        if tipo_comprobante == "01" and not serie.startswith("F"):
            errores.append("La serie de factura debe iniciar con F. Ejemplo: F001.")

        if tipo_comprobante == "03" and not serie.startswith("B"):
            errores.append("La serie de boleta debe iniciar con B. Ejemplo: B001.")

        try:
            correlativo_actual = int(correlativo_actual)
            if correlativo_actual < 0:
                errores.append("El correlativo actual no puede ser negativo.")
        except ValueError:
            errores.append("El correlativo actual debe ser un número válido.")

        sucursal = None
        if sucursal_id:
            sucursal = Sucursal.objects.filter(id=sucursal_id, farmacia=farmacia).first()
            if not sucursal:
                errores.append("La sucursal seleccionada no pertenece a esta farmacia.")

        if not errores:
            existe = SerieComprobante.objects.filter(
                farmacia=farmacia,
                sucursal=sucursal,
                tipo_comprobante=tipo_comprobante,
                serie=serie,
                ambiente=ambiente,
            ).exclude(id=serie_obj.id).exists()

            if existe:
                errores.append("Ya existe una serie igual para esta sucursal, tipo y ambiente.")

        if errores:
            context = {
                "farmacia": farmacia,
                "sucursales": sucursales,
                "serie_obj": serie_obj,
                "errores": errores,
                "serie_data": request.POST,
                "modo": "editar",
            }
            return render(request, "farmacias_main_templates/series_form.html", context)

        serie_obj.sucursal = sucursal
        serie_obj.tipo_comprobante = tipo_comprobante
        serie_obj.serie = serie
        serie_obj.correlativo_actual = correlativo_actual
        serie_obj.ambiente = ambiente
        serie_obj.activo = activo
        serie_obj.save()

        return redirect("core:series_list", farmacia_id=farmacia.id)

    context = {
        "farmacia": farmacia,
        "sucursales": sucursales,
        "serie_obj": serie_obj,
        "modo": "editar",
    }

    return render(request, "farmacias_main_templates/series_form.html", context)


@login_required
@require_POST
def serie_delete_view(request, pk):
    serie_obj = get_object_or_404(SerieComprobante, pk=pk)
    farmacia_id = serie_obj.farmacia_id
    serie_obj.delete()

    return redirect("core:series_list", farmacia_id=farmacia_id)


def dashboard_view(request):
    if not request.user.is_authenticated:
        return redirect('core:login')
        
    return render(request, 'farmacias_main_templates/dashboard.html', {
        'farmacia': getattr(request.user, 'farmacia', None)
    })