# ventas/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views # Para las vistas web tradicionales (ej. ventas_home_view)
from . import api_views # Para las vistas de la API

# Crea un router y registra nuestros ViewSets con él.
router = DefaultRouter()
router.register(r'ventas', api_views.VentaViewSet)
router.register(r'detalles-venta', api_views.DetalleVentaViewSet) # Si se gestionan detalles individualmente


app_name = 'ventas' # Define un espacio de nombres para las URLs de esta app

urlpatterns = [
    # URLs para vistas web tradicionales (si las tienes)
    path('', views.ventas_home_view, name='home'),

    # URLs para la API REST de la aplicación 'ventas'
    # Las URLs generadas por el router se incluyen aquí bajo un prefijo 'api/'
    path('api/', include(router.urls)),
]
