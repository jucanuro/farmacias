from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import api_views

router = DefaultRouter()
router.register(r'roles', api_views.RolViewSet)
router.register(r'usuarios', api_views.UsuarioViewSet, basename='usuario')
router.register(r'configuraciones-fe', api_views.ConfiguracionFacturacionElectronicaViewSet)
router.register(r'farmacias', api_views.FarmaciaViewSet)
router.register(r'sucursales', api_views.SucursalViewSet)

app_name = 'core'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('api/', include(router.urls)),
    path('api/registro/', views.registro_api_view, name='api_registro'),
    path('api/login/', views.login_api_view, name='api_login'),
    path('logout/', views.logout_view, name='logout'),
    
    # URLs de Gestión de Farmacias
    path('farmacias/', views.farmacias_list_view, name='farmacias_list'),
    path('farmacias/nueva/', views.farmacia_create_view, name='farmacia_create'),
    path('farmacias/<int:pk>/editar/', views.farmacia_update_view, name='farmacia_update'),
    path('farmacias/<int:pk>/eliminar/', views.farmacia_delete_view, name='farmacia_delete'),
    
    # URLs de Gestión de Sucursales
    path('farmacias/<int:farmacia_id>/sucursales/', views.sucursal_list_view, name='sucursal_list'),
    path('farmacias/<int:farmacia_id>/sucursales/nueva/', views.sucursal_create_view, name='sucursal_create'),
    path('sucursales/<int:pk>/editar/', views.sucursal_update_view, name='sucursal_update'),
    path('sucursales/<int:pk>/eliminar/', views.sucursal_delete_view, name='sucursal_delete'),
    
    # URLs de Gestión de Roles
        
    path('roles/', views.rol_list_view, name='rol_list'), 
    path('roles/nuevo/', views.rol_create_view, name='rol_create'),
    path('roles/<int:pk>/editar/', views.rol_update_view, name='rol_update'), 
    path('roles/<int:pk>/eliminar/', views.rol_delete_view, name='rol_delete'),
    
    # URLs de Gestión de Usuarios
    
    path('usuarios/', views.usuario_list_view, name='usuario_list'),
    path('usuarios/nuevo/', views.usuario_create_view, name='usuario_create'),
    path('usuarios/<int:pk>/editar/', views.usuario_update_view, name='usuario_update'),
    path('usuarios/<int:pk>/toggle-active/', views.usuario_toggle_active_view, name='usuario_toggle_active'),
    
]
