from django.urls import path
from . import views

app_name = 'ventas'

urlpatterns = [
    path('pos/', views.pos_view, name='pos'),
    path('listado/', views.venta_list_view, name='venta_list'),
    path('comprobante/<int:venta_id>/pdf/', views.generar_comprobante_pdf, name='generar_comprobante_pdf'),
]