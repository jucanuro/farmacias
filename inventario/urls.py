# inventario/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views # Para las vistas web tradicionales (ej. inventario_home_view)
from . import api_views # Para las vistas de la API

# Crea un router y registra nuestros ViewSets con él.
router = DefaultRouter()
router.register(r'categorias', api_views.CategoriaProductoViewSet)
router.register(r'laboratorios', api_views.LaboratorioViewSet)
router.register(r'principios-activos', api_views.PrincipioActivoViewSet)
router.register(r'formas-farmaceuticas', api_views.FormaFarmaceuticaViewSet)
router.register(r'productos', api_views.ProductoViewSet)
router.register(r'stocks', api_views.StockProductoViewSet)
router.register(r'movimientos', api_views.MovimientoInventarioViewSet)


app_name = 'inventario' # Define un espacio de nombres para las URLs de esta app

urlpatterns = [
    # URLs para vistas web tradicionales (si las tienes)
    path('', views.inventario_home_view, name='home'),

    # URLs para la API REST de la aplicación 'inventario'
    # Las URLs generadas por el router se incluyen aquí bajo un prefijo 'api/'
    path('api/', include(router.urls)),
]
