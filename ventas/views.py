# ventas/views.py

from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from weasyprint import HTML
import inspect
from .models import Venta

@login_required
def pos_view(request):
    """
    Renderiza la interfaz principal del Punto de Venta (POS).
    Toda la lógica será manejada por JavaScript.
    """
    return render(request, 'ventas_templates/pos.html')

@login_required
def venta_list_view(request):
    """
    Renderiza la página que mostrará el listado de ventas.
    La carga de datos se hará con JavaScript y la API.
    """
    return render(request, 'ventas_templates/venta_list.html')


def generar_comprobante_pdf(request, venta_id):
    """
    Toma una venta_id, renderiza una plantilla HTML con sus datos
    y devuelve un archivo PDF como respuesta.
    """
    try:
        venta = Venta.objects.select_related(
            'cliente', 
            'vendedor', 
            'sucursal__farmacia'  # <-- ESTA ES LA LÍNEA CORREGIDA FINAL
        ).get(pk=venta_id)
        
        # Accedemos a los objetos usando los nombres de campo correctos
        sucursal = venta.sucursal
        # Usamos el campo 'farmacia' para obtener los datos de la empresa
        empresa = venta.sucursal.farmacia 

        context = {
            'venta': venta,
            'detalles': venta.detalles.all(),
            'empresa': empresa, # Le pasamos el objeto empresa/farmacia
            'sucursal': sucursal,
        }

        html_string = render_to_string('ventas_templates/comprobante_template.html', context)
        print("DEBUG: Usando la clase HTML:", HTML)
        print("DEBUG: Ubicación del archivo:", inspect.getfile(HTML))
        pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf()

        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="comprobante_venta_{venta.id}.pdf"'
        
        return response

    except Venta.DoesNotExist:
        raise Http404("La venta especificada no existe.")
    except Exception as e:
        return HttpResponse(f"Ocurrió un error al generar el PDF: {e}", status=500)