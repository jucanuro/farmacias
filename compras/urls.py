from django.urls import path
from . import views

app_name = 'compras'

urlpatterns = [
    path('', views.compras_home_view, name='home'),
    path('nueva/', views.compra_create_view, name='compra_create'),
    path('<int:pk>/editar/', views.compra_edit_view, name='compra_edit'),
    path('<int:pk>/eliminar/', views.compra_delete_view, name='compra_delete'),
]