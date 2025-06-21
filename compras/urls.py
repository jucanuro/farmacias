# compras/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views # Para las vistas web tradicionales (ej. compras_home_view)
from . import api_views # Para las vistas de la API

# Crea un router y registra nuestros ViewSets con él.
router = DefaultRouter()
router.register(r'cotizaciones', api_views.CotizacionProveedorViewSet)
router.register(r'detalles-cotizacion', api_views.DetalleCotizacionViewSet) # Si se gestionan detalles individualmente
router.register(r'ordenes', api_views.OrdenCompraViewSet)
router.register(r'detalles-orden', api_views.DetalleOrdenCompraViewSet) # Si se gestionan detalles individualmente
router.register(r'compras', api_views.CompraViewSet)
router.register(r'detalles-compra', api_views.DetalleCompraViewSet) # Si se gestionan detalles individualmente


app_name = 'compras' # Define un espacio de nombres para las URLs de esta app

urlpatterns = [
    # URLs para vistas web tradicionales (si las tienes)
    path('', views.compras_home_view, name='home'),

    # URLs para la API REST de la aplicación 'compras'
    # Las URLs generadas por el router se incluyen aquí bajo un prefijo 'api/'
    path('api/', include(router.urls)),
]
