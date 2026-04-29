from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, ProtectedError
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from .models import Proveedor


def proveedor_list_view(request):
    query = request.GET.get('q', '').strip()
    estado = request.GET.get('estado', 'activos').strip()

    proveedores = Proveedor.objects.all().order_by('nombre_comercial')

    if estado == 'activos':
        proveedores = proveedores.filter(activo=True)
    elif estado == 'inactivos':
        proveedores = proveedores.filter(activo=False)

    if query:
        proveedores = proveedores.filter(
            Q(nombre_comercial__icontains=query) |
            Q(razon_social__icontains=query) |
            Q(numero_documento__icontains=query) |
            Q(telefono__icontains=query) |
            Q(email__icontains=query) |
            Q(persona_contacto__icontains=query)
        )

    paginator = Paginator(proveedores, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'proveedores_templates/proveedor_list.html', {
        'proveedores': page_obj,
        'query': query,
        'estado': estado,
        'total_proveedores': proveedores.count(),
    })


def proveedor_create_view(request):
    return proveedor_form_view(request)


def proveedor_update_view(request, pk):
    proveedor = get_object_or_404(Proveedor, pk=pk)
    return proveedor_form_view(request, proveedor)


def proveedor_form_view(request, proveedor=None):
    if request.method == 'POST':
        nombre_comercial = request.POST.get('nombre_comercial', '').strip()
        razon_social = request.POST.get('razon_social', '').strip()
        tipo_documento = request.POST.get('tipo_documento', '').strip()
        numero_documento = request.POST.get('numero_documento', '').strip()
        direccion = request.POST.get('direccion', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        email = request.POST.get('email', '').strip()
        sitio_web = request.POST.get('sitio_web', '').strip()
        persona_contacto = request.POST.get('persona_contacto', '').strip()
        telefono_contacto = request.POST.get('telefono_contacto', '').strip()
        condiciones_pago = request.POST.get('condiciones_pago', '').strip()
        activo = request.POST.get('activo') == 'on'

        errores = []

        if not nombre_comercial:
            errores.append('El nombre comercial es obligatorio.')

        if not tipo_documento:
            errores.append('El tipo de documento es obligatorio.')

        if not numero_documento:
            errores.append('El número de documento es obligatorio.')

        existe_documento = Proveedor.objects.filter(numero_documento=numero_documento)
        if proveedor:
            existe_documento = existe_documento.exclude(pk=proveedor.pk)

        if numero_documento and existe_documento.exists():
            errores.append('Ya existe un proveedor con ese número de documento.')

        if errores:
            for error in errores:
                messages.error(request, error)
        else:
            if proveedor is None:
                proveedor = Proveedor()

            proveedor.nombre_comercial = nombre_comercial
            proveedor.razon_social = razon_social
            proveedor.tipo_documento = tipo_documento
            proveedor.numero_documento = numero_documento
            proveedor.direccion = direccion
            proveedor.telefono = telefono
            proveedor.email = email
            proveedor.sitio_web = sitio_web
            proveedor.persona_contacto = persona_contacto
            proveedor.telefono_contacto = telefono_contacto
            proveedor.condiciones_pago = condiciones_pago
            proveedor.activo = activo
            proveedor.save()

            if proveedor.pk:
                messages.success(request, f"El proveedor '{proveedor.nombre_comercial}' fue guardado correctamente.")

            return redirect('proveedores:proveedor_list')

    return render(request, 'proveedores_templates/proveedor_form.html', {
        'proveedor': proveedor,
    })


@require_POST
def proveedor_delete_view(request, pk):
    proveedor = get_object_or_404(Proveedor, pk=pk)

    try:
        nombre = proveedor.nombre_comercial
        proveedor.delete()
        messages.success(request, f"El proveedor '{nombre}' fue eliminado correctamente.")
    except ProtectedError:
        messages.error(
            request,
            f"El proveedor '{proveedor.nombre_comercial}' no se puede eliminar porque está asociado a otros registros."
        )

    return redirect('proveedores:proveedor_list')