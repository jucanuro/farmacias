# traslados/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import api_views

# 1. El router solo debe registrar los ViewSets completos
router = DefaultRouter()
router.register(r'transferencias', api_views.TransferenciaViewSet, basename='transferencia')

app_name = 'traslados'

urlpatterns = [
    # URLs para las vistas web
    path('', views.traslados_home_view, name='home'),
    path('nuevo/', views.traslado_create_view, name='traslado_create'), 

    # URLs de la API generadas por el router
    path('api/', include(router.urls)),
    
    # 2. La vista de autocompletado se añade aquí, como una URL normal
    path('api/stock-autocomplete/', api_views.StockAutocompleteAPIView.as_view(), name='stock-autocomplete'),
]