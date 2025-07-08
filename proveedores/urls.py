from django.urls import path
from . import views

app_name = 'proveedores'

urlpatterns = [
    path('', views.proveedor_list_view, name='proveedor_list'),
    path('nuevo/', views.proveedor_create_view, name='proveedor_create'),
    path('<int:pk>/editar/', views.proveedor_update_view, name='proveedor_update'),
    path('<int:pk>/eliminar/', views.proveedor_delete_view, name='proveedor_delete'),
]