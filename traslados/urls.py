from django.urls import path
from . import views

app_name = "traslados"

urlpatterns = [
    path("", views.traslados_home_view, name="traslados_home"),
    path("nuevo/", views.traslado_create_view, name="traslado_create"),
    path("<int:transferencia_id>/editar/", views.traslado_edit_view, name="traslado_edit"),

    path("api/transferencias/", views.transferencias_list_api, name="transferencias_list_api"),
    path("api/transferencias/crear/", views.transferencia_create_api, name="transferencia_create_api"),
    path("api/transferencias/<int:transferencia_id>/", views.transferencia_detail_api, name="transferencia_detail_api"),
    path("api/transferencias/<int:transferencia_id>/editar/", views.transferencia_update_api, name="transferencia_update_api"),
    path("api/transferencias/<int:transferencia_id>/eliminar/", views.transferencia_delete_api, name="transferencia_delete_api"),
    path("api/transferencias/<int:transferencia_id>/enviar/", views.transferencia_enviar_api, name="transferencia_enviar_api"),
    path("api/transferencias/<int:transferencia_id>/recibir/", views.transferencia_recibir_api, name="transferencia_recibir_api"),
    
]