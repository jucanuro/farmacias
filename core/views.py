import json
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login, logout
from rest_framework.authtoken.models import Token
from django.contrib.auth.decorators import login_required

from .forms import (
    CustomUserCreationForm,
    FarmaciaForm,
    SucursalForm,
    RolForm,
    UsuarioCreateForm,
    UsuarioUpdateForm,
    ConfiguracionFacturacionForm
)
from .models import Farmacia, Sucursal, Rol, Usuario, ConfiguracionFacturacionElectronica, SerieComprobante


def enviar_factura_service(invoice_data, configuracion):
    if invoice_data and configuracion:
        return {'success': True, 'invoice_id': 'INV-12345'}
    return {'success': False, 'error': 'Datos de factura o configuración faltantes'}


def home_view(request):
    return render(request, 'landing.html')

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