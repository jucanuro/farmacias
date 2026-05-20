from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include 
from rest_framework.authtoken.views import obtain_auth_token
from django.views.generic import TemplateView 

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),

    path('core/', include('core.urls')),
    path('inventario/', include('inventario.urls')),
    path('clientes/', include('clientes.urls')),
    path('proveedores/', include('proveedores.urls')),
    path('compras/', include('compras.urls')),
    path('ventas/', include('ventas.urls')),
    path('traslados/', include('traslados.urls')),
    path("facturacion/", include("facturacion.urls")),
    path('ia/', include('ia_assistant.urls')),

    path('', TemplateView.as_view(template_name='landing.html'), name='landing'),
    path('login/', TemplateView.as_view(template_name='farmacias_main_templates/index.html'), name='login'),
    path('dashboard/', TemplateView.as_view(template_name='farmacias_main_templates/dashboard.html'), name='dashboard'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
