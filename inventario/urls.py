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
    path('categorias/', views.categoria_list_view, name='categoria_list'),
    path('categorias/nueva/', views.categoria_create_view, name='categoria_create'),
    path('categorias/<int:pk>/editar/', views.categoria_update_view, name='categoria_update'),


    
    path('api/', include(router.urls)),
]