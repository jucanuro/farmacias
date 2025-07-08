from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import api_views

router = DefaultRouter()
router.register(r'cotizaciones', api_views.CotizacionProveedorViewSet)
router.register(r'detalles-cotizacion', api_views.DetalleCotizacionViewSet)
router.register(r'ordenes', api_views.OrdenCompraViewSet)
router.register(r'detalles-orden', api_views.DetalleOrdenCompraViewSet)
router.register(r'compras', api_views.CompraViewSet)
router.register(r'detalles-compra', api_views.DetalleCompraViewSet)

app_name = 'compras'

urlpatterns = [
    path('', views.compras_home_view, name='home'),
    path('nueva/', views.compra_create_view, name='compra_create'),

    path('api/', include(router.urls)),
]