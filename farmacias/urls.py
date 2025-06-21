# your_project_name/urls.py
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include # Asegúrate de importar 'include'
from rest_framework.authtoken.views import obtain_auth_token

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
        
    # *** CAMBIO AQUI ***
    # Esto le dice a Django que las URLs que comienzan con 'core/' deben ser manejadas
    # por el archivo core.urls de tu aplicación.
    path('core/', include('core.urls')), 
    # *******************

    path('inventario/', include('inventario.urls')), 
    path('clientes/', include('clientes.urls')),
    path('proveedores/', include('proveedores.urls')),
    path('compras/', include('compras.urls')),
    path('ventas/', include('ventas.urls')),
    path('traslados/', include('traslados.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
