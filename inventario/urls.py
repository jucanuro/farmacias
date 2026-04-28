from django.urls import path
from . import views

app_name = 'inventario'

urlpatterns = [
    path('', views.inventario_home_view, name='home'),

    path('productos/', views.producto_list_view, name='producto_list'),
    path('productos/nuevo/', views.producto_form_view, name='producto_create'),
    path('productos/<int:pk>/', views.producto_detail_view, name='producto_detail'),
    path('productos/<int:pk>/editar/', views.producto_form_view, name='producto_update'),

    path('categorias/', views.categoria_list_view, name='categoria_list'),
    path('categorias/nueva/', views.categoria_create_view, name='categoria_create'),
    path('categorias/<int:pk>/editar/', views.categoria_update_view, name='categoria_update'),
    path('categorias/<int:pk>/eliminar/', views.categoria_delete_view, name='categoria_delete'),

    path('laboratorios/', views.laboratorio_list_view, name='laboratorio_list'),
    path('laboratorios/nuevo/', views.laboratorio_create_view, name='laboratorio_create'),
    path('laboratorios/<int:pk>/editar/', views.laboratorio_update_view, name='laboratorio_update'),
    path('laboratorios/<int:pk>/eliminar/', views.laboratorio_delete_view, name='laboratorio_delete'),

    path('formas-farmaceuticas/', views.forma_farmaceutica_list_view, name='forma_farmaceutica_list'),
    path('formas-farmaceuticas/nueva/', views.forma_farmaceutica_create_view, name='forma_farmaceutica_create'),
    path('formas-farmaceuticas/<int:pk>/editar/', views.forma_farmaceutica_update_view, name='forma_farmaceutica_update'),
    path('formas-farmaceuticas/<int:pk>/eliminar/', views.forma_farmaceutica_delete_view, name='forma_farmaceutica_delete'),

    path('principios-activos/', views.principio_activo_list_view, name='principio_activo_list'),
    path('principios-activos/nuevo/', views.principio_activo_create_view, name='principio_activo_create'),
    path('principios-activos/<int:pk>/editar/', views.principio_activo_update_view, name='principio_activo_update'),
    path('principios-activos/<int:pk>/eliminar/', views.principio_activo_delete_view, name='principio_activo_delete'),

    path('unidades/', views.unidad_presentacion_list_view, name='unidad_presentacion_list'),
    path('unidades/nueva/', views.unidad_presentacion_create_view, name='unidad_presentacion_create'),
    path('unidades/<int:pk>/editar/', views.unidad_presentacion_update_view, name='unidad_presentacion_update'),
    path('unidades/<int:pk>/eliminar/', views.unidad_presentacion_delete_view, name='unidad_presentacion_delete'),
]