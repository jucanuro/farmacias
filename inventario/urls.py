from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import api_views

router = DefaultRouter()
router.register(r'categorias', api_views.CategoriaProductoViewSet)
router.register(r'laboratorios', api_views.LaboratorioViewSet)
router.register(r'principios-activos', api_views.PrincipioActivoViewSet)
router.register(r'formas-farmaceuticas', api_views.FormaFarmaceuticaViewSet)
router.register(r'productos', api_views.ProductoViewSet)
router.register(r'stocks', api_views.StockProductoViewSet)
router.register(r'movimientos', api_views.MovimientoInventarioViewSet)

app_name = 'inventario'

urlpatterns = [
    path('', views.inventario_home_view, name='home'),
    
    #Gestión de Categorías
    path('categorias/', views.categoria_list_view, name='categoria_list'),
    path('categorias/nueva/', views.categoria_create_view, name='categoria_create'),
    path('categorias/<int:pk>/editar/', views.categoria_update_view, name='categoria_update'),
    path('categorias/<int:pk>/eliminar/', views.categoria_delete_view, name='categoria_delete'),
    
    #Gestión de Laboratorios
    path('laboratorios/', views.laboratorio_list_view, name='laboratorio_list'),
    path('laboratorios/nuevo/', views.laboratorio_create_view, name='laboratorio_create'),
    path('laboratorios/<int:pk>/editar/', views.laboratorio_update_view, name='laboratorio_update'),
    path('laboratorios/<int:pk>/eliminar/', views.laboratorio_delete_view, name='laboratorio_delete'),
    
    #Gestión de formas 
    path('formas-farmaceuticas/', views.forma_farmaceutica_list_view, name='forma_farmaceutica_list'),
    path('formas-farmaceuticas/nueva/', views.forma_farmaceutica_create_view, name='forma_farmaceutica_create'),
    path('formas-farmaceuticas/<int:pk>/editar/', views.forma_farmaceutica_update_view, name='forma_farmaceutica_update'),
    path('formas-farmaceuticas/<int:pk>/eliminar/', views.forma_farmaceutica_delete_view, name='forma_farmaceutica_delete'),
    
    #Gestión de principios
    
    path('principios-activos/', views.principio_activo_list_view, name='principio_activo_list'),
    path('principios-activos/nuevo/', views.principio_activo_create_view, name='principio_activo_create'),
    path('principios-activos/<int:pk>/editar/', views.principio_activo_update_view, name='principio_activo_update'),
    path('principios-activos/<int:pk>/eliminar/', views.principio_activo_delete_view, name='principio_activo_delete'),

    # Gestión de productos
    
    path('productos/', views.producto_list_view, name='producto_list'),
    path('productos/nuevo/', views.producto_create_view, name='producto_create'),
    path('productos/<int:pk>/editar/', views.producto_update_view, name='producto_update'),









    
    path('api/', include(router.urls)),
]