# clientes/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import api_views

router = DefaultRouter()
# El basename es importante para que Django pueda generar las URLs automáticamente
router.register(r'clientes', api_views.ClienteViewSet, basename='cliente')

app_name = 'clientes'

urlpatterns = [
    # URLs para la API REST
    path('api/', include(router.urls)),

    # --- URLs para la Interfaz de Usuario ---
    path('', views.clientes_home_view, name='lista'), # Cambiado a 'lista' por claridad
    path('nuevo/', views.cliente_form_view, name='crear'), # <-- AÑADIDA
    path('<int:pk>/editar/', views.cliente_form_view, name='editar'), # <-- AÑADIDA
]