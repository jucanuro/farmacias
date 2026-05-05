from django.urls import path
from . import views

app_name = "facturacion"

urlpatterns = [
    path(
        "api/comprobantes/crear-desde-venta/",
        views.crear_desde_venta_api,
        name="crear_desde_venta_api"
    ),
    path(
        "api/comprobantes/venta/<int:venta_id>/",
        views.comprobante_por_venta_api,
        name="comprobante_por_venta_api"
    ),
    
    path(
        "api/comprobantes/<int:comprobante_id>/generar-xml/",
        views.generar_xml_api,
        name="generar_xml_api"
    ),
]