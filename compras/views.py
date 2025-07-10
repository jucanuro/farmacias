# compras/api_views.py

# Importaciones de Django y REST Framework
from rest_framework import viewsets, permissions, filters, status
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

# Importaciones de tus Modelos (¡LA CLAVE ESTÁ AQUÍ!)
from .models import (
    CotizacionProveedor, DetalleCotizacion,
    OrdenCompra, DetalleOrdenCompra,
    Compra, DetalleCompra, Proveedor, Sucursal
)
# Importaciones de tus Serializers
from .serializers import (
    CotizacionProveedorSerializer, DetalleCotizacionSerializer,
    OrdenCompraSerializer, DetalleOrdenCompraSerializer,
    CompraSerializer, DetalleCompraSerializer
)
# Otras importaciones
from core.permissions import IsAdminOrManager
from inventario.models import StockProducto, MovimientoInventario

# Create your views here.
def compras_home_view(request):
    """
    Muestra la página con el listado de compras.
    Los datos se cargarán dinámicamente con JavaScript.
    """
    return render(request, 'compras_templates/compras_home.html')

def compra_create_view(request):
    """
    Prepara y muestra el formulario para registrar una nueva compra.
    """
    proveedores = Proveedor.objects.filter(activo=True).order_by('nombre_comercial')
    sucursales = Sucursal.objects.all().order_by('nombre')
    
    context = {
        'proveedores': proveedores,
        'sucursales': sucursales,
    }
    return render(request, 'compras_templates/compra_form.html', context)


class DetalleCompraViewSet(viewsets.ModelViewSet):
    """
    API endpoint para gestionar Detalles de Compras.
    """
    queryset = DetalleCompra.objects.all().order_by('compra', 'producto__nombre', 'lote')
    serializer_class = DetalleCompraSerializer
    permission_classes = [IsAdminOrManager]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['compra', 'producto', 'lote', 'fecha_vencimiento']
    search_fields = ['producto__nombre', 'lote', 'compra__numero_factura_proveedor']
    ordering_fields = ['cantidad_recibida', 'fecha_vencimiento']

    # La lógica de get_queryset está bien, la dejamos como está
    def get_queryset(self):
        # ... tu código actual aquí ...
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_authenticated and not user.is_superuser and user.rol:
            if user.rol.nombre == 'Administrador':
                return queryset
            elif user.rol.nombre == 'Gerente de Sucursal' and user.sucursal:
                return queryset.filter(compra__sucursal_destino=user.sucursal)
            else:
                return queryset.none()
        return queryset.none()

    # --- NUEVOS MÉTODOS PARA ACTUALIZAR TOTALES ---
    
    def perform_create(self, serializer):
        """ Al crear un detalle, recalcula los totales de la compra padre. """
        detalle = serializer.save()
        if detalle.compra:
            detalle.compra.calcular_totales()

    def perform_update(self, serializer):
        """ Al actualizar un detalle, recalcula los totales de la compra padre. """
        detalle = serializer.save()
        if detalle.compra:
            detalle.compra.calcular_totales()

    def perform_destroy(self, instance):
        """ Al eliminar un detalle, recalcula los totales de la compra padre. """
        compra_padre = instance.compra
        instance.delete()
        if compra_padre:
            compra_padre.calcular_totales()
            
            
            
            
def compra_edit_view(request, pk):
    """
    Prepara y muestra el formulario para editar una compra existente.
    """
    compra = get_object_or_404(Compra, pk=pk)
    
    # --- PASO 1: SERIALIZA EL OBJETO COMPRA ---
    serializer = CompraSerializer(compra)
    
    proveedores = Proveedor.objects.filter(activo=True).order_by('nombre_comercial')
    sucursales = Sucursal.objects.all().order_by('nombre')
    
    context = {
        'compra': compra, # Mantenemos el objeto para usarlo en el título, etc.
        'compra_json': serializer.data, # ¡Pasamos los datos serializados a la plantilla!
        'proveedores': proveedores,
        'sucursales': sucursales,
    }
    return render(request, 'compras_templates/compra_form.html', context)