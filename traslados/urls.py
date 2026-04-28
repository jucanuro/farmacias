from django.urls import path
from . import views

app_name = 'traslados'

urlpatterns = [
    path('', views.traslados_home_view, name='home'),
    path('nuevo/', views.traslado_create_view, name='traslado_create'),
]