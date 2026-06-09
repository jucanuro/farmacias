from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home_view, name='home'),

    path('registro/', views.registro_view, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('farmacias/', views.farmacias_list_view, name='farmacias_list'),
    path('farmacias/nueva/', views.farmacia_create_view, name='farmacia_create'),
    path('farmacias/<int:pk>/editar/', views.farmacia_update_view, name='farmacia_update'),
    path('farmacias/<int:pk>/eliminar/', views.farmacia_delete_view, name='farmacia_delete'),

    path('farmacias/<int:farmacia_id>/sucursales/', views.sucursal_list_view, name='sucursal_list'),
    path('farmacias/<int:farmacia_id>/sucursales/nueva/', views.sucursal_create_view, name='sucursal_create'),
    path('sucursales/<int:pk>/editar/', views.sucursal_update_view, name='sucursal_update'),
    path('sucursales/<int:pk>/eliminar/', views.sucursal_delete_view, name='sucursal_delete'),

    path('roles/', views.rol_list_view, name='rol_list'),
    path('roles/nuevo/', views.rol_create_view, name='rol_create'),
    path('roles/<int:pk>/editar/', views.rol_update_view, name='rol_update'),
    path('roles/<int:pk>/eliminar/', views.rol_delete_view, name='rol_delete'),

    path('usuarios/', views.usuario_list_view, name='usuario_list'),
    path('usuarios/nuevo/', views.usuario_create_view, name='usuario_create'),
    path('usuarios/<int:pk>/editar/', views.usuario_update_view, name='usuario_update'),
    path('usuarios/<int:pk>/toggle-active/', views.usuario_toggle_active_view, name='usuario_toggle_active'),

    path('configuracion-fe/', views.configuracion_facturacion_view, name='configuracion_facturacion'),
    path('enviar-factura/', views.enviar_factura_electronica_view, name='enviar_factura_electronica'),

    path('farmacias/<int:farmacia_id>/series/', views.series_list_view, name='series_list'),
    path('farmacias/<int:farmacia_id>/series/nueva/', views.serie_create_view, name='serie_create'),
    path('series/<int:pk>/editar/', views.serie_update_view, name='serie_update'),
    path('series/<int:pk>/eliminar/', views.serie_delete_view, name='serie_delete'),
    
    path('dashboard/', views.dashboard_view, name='dashboard'),
]