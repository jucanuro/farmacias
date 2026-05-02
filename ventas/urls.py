# ventas/urls.py

from django.urls import path
from . import views

app_name = 'ventas'

urlpatterns = [
    path('pos/', views.pos_view, name='pos'),
    path('listado/', views.venta_list_view, name='venta_list'),

    path(
        'comprobante/<int:venta_id>/pdf/',
        views.generar_comprobante_pdf,
        name='generar_comprobante_pdf'
    ),

    path('api/caja/estado/', views.estado_caja_api, name='estado_caja_api'),
    path('api/caja/abrir/', views.abrir_caja_api, name='abrir_caja_api'),
    path('api/caja/cerrar/', views.cerrar_caja_api, name='cerrar_caja_api'),

    path('api/ventas/registrar/', views.registrar_venta_api, name='registrar_venta_api'),
    path('api/ventas/<int:venta_id>/', views.venta_detail_api, name='venta_detail_api'),
    path('api/ventas/', views.ventas_list_api, name='ventas_list_api'),
]