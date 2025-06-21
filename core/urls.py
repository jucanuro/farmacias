# core/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views # Para las vistas web tradicionales (ej. home_view)
from . import api_views # Para las vistas de la API

# Crea un router y registra nuestros ViewSets con él.
router = DefaultRouter()
router.register(r'roles', api_views.RolViewSet)
router.register(r'usuarios', api_views.UsuarioViewSet)
router.register(r'configuraciones-fe', api_views.ConfiguracionFacturacionElectronicaViewSet)
router.register(r'farmacias', api_views.FarmaciaViewSet)
router.register(r'sucursales', api_views.SucursalViewSet)


app_name = 'core' # Define un espacio de nombres para las URLs de esta app

urlpatterns = [
    # URLs para vistas web tradicionales (si las tienes)
    path('', views.home_view, name='home'),

    # URLs para la API REST de la aplicación 'core'
    # Las URLs generadas por el router se incluyen aquí
    path('api/', include(router.urls)), # Prefijo para las URLs de la API de core
]
