from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include # Asegúrate de importar 'include'
from rest_framework.authtoken.views import obtain_auth_token
from django.views.generic import TemplateView # <-- ¡Importa esto para servir tus templates!

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
        
    # URLs de tus aplicaciones
    path('core/', include('core.urls')), 
    path('inventario/', include('inventario.urls')), 
    path('clientes/', include('clientes.urls')),
    path('proveedores/', include('proveedores.urls')),
    path('compras/', include('compras.urls')),
    path('ventas/', include('ventas.urls')),
    path('traslados/', include('traslados.urls')),

    # *** NUEVAS URLS PARA TUS TEMPLATES HTML/JS ***
    # La página de login (la raíz de tu sitio)
    path('', TemplateView.as_view(template_name='farmacias_main_templates/index.html'), name='login'), 
    # La página del dashboard, accesible después de iniciar sesión
    path('dashboard/', TemplateView.as_view(template_name='farmacias_main_templates/dashboard.html'), name='dashboard'),
    # **********************************************
]

# Configuración para servir archivos estáticos y de medios durante el desarrollo (DEBUG=True)
if settings.DEBUG:
    # Para servir los archivos de media (subidas de usuarios, etc.)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # Para servir los archivos estáticos de STATICFILES_DIRS (tu carpeta 'static')
    # Esto es crucial para que Django encuentre 'style.css', 'farmacias.html', 'sucursales.html'
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
