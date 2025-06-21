# traslados/admin.py

from django.contrib import admin
from .models import TransferenciaStock
from django.utils import timezone # Para usar timezone.now()
from django.db import transaction # Para transacciones atómicas

@admin.register(TransferenciaStock)
class TransferenciaStockAdmin(admin.ModelAdmin):
    list_display = (
        'producto', 'sucursal_origen', 'sucursal_destino', 'cantidad',
        'fecha_solicitud', 'estado', 'enviado_por', 'recibido_por'
    )
    list_filter = (
        'estado', 'sucursal_origen__farmacia', 'sucursal_origen',
        'sucursal_destino__farmacia', 'sucursal_destino', 'fecha_solicitud'
    )
    search_fields = (
        'producto__nombre', 'sucursal_origen__nombre', 'sucursal_destino__nombre',
        'solicitado_por__username', 'observaciones'
    )
    raw_id_fields = (
        'producto', 'sucursal_origen', 'sucursal_destino',
        'solicitado_por', 'enviado_por', 'recibido_por'
    )
    readonly_fields = ('fecha_solicitud', 'fecha_envio', 'fecha_recepcion')
    date_hierarchy = 'fecha_solicitud'
    ordering = ('-fecha_solicitud',)
    actions = ['marcar_como_enviado', 'marcar_como_recibido', 'marcar_como_rechazado']

    # Sobrescribimos save_model para ejecutar validaciones antes de guardar
    def save_model(self, request, obj, form, change):
        if not obj.pk: # Asigna el usuario que solicita la transferencia si es una nueva
            obj.solicitado_por = request.user
        try:
            obj.limpiar_y_validar_sucursales() # Valida que no sean la misma sucursal y pertenezcan a la misma Farmacia
            super().save_model(request, obj, form, change)
        except ValueError as e:
            self.message_user(request, f"Error al guardar la transferencia: {e}", level='error')
            # Es importante manejar este error para que no detenga el flujo del admin
            # raise # No relanzar para que el admin muestre el error de forma amigable


    def marcar_como_enviado(self, request, queryset):
        for transferencia in queryset:
            if transferencia.estado == 'PENDIENTE':
                try:
                    transferencia.realizar_envio(request.user)
                    self.message_user(request, f"Transferencia {transferencia.id} marcada como ENVIADA y stock de origen decrementado.", level='success')
                except ValueError as e:
                    self.message_user(request, f"Error al enviar transferencia {transferencia.id}: {e}", level='error')
                except Exception as e:
                    self.message_user(request, f"Error inesperado al enviar transferencia {transferencia.id}: {e}", level='error')
            else:
                self.message_user(request, f"Transferencia {transferencia.id} no puede ser enviada. Estado actual: {transferencia.estado}.", level='warning')
    marcar_como_enviado.short_description = "Marcar seleccionados como Enviados (Decrementa stock origen)"


    def marcar_como_recibido(self, request, queryset):
        for transferencia in queryset:
            if transferencia.estado == 'ENVIADO':
                try:
                    transferencia.realizar_recepcion(request.user)
                    self.message_user(request, f"Transferencia {transferencia.id} marcada como RECIBIDA y stock de destino incrementado.", level='success')
                except ValueError as e:
                    self.message_user(request, f"Error al recibir transferencia {transferencia.id}: {e}", level='error')
                except Exception as e:
                    self.message_user(request, f"Error inesperado al recibir transferencia {transferencia.id}: {e}", level='error')
            else:
                self.message_user(request, f"Transferencia {transferencia.id} no puede ser recibida. Estado actual: {transferencia.estado}.", level='warning')
    marcar_como_recibido.short_description = "Marcar seleccionados como Recibidos (Incrementa stock destino)"

    def marcar_como_rechazado(self, request, queryset):
        for transferencia in queryset:
            if transferencia.estado in ['PENDIENTE', 'ENVIADO']:
                try:
                    # Se podría pedir una observación para el rechazo si fuera necesario
                    transferencia.rechazar_transferencia(request.user)
                    self.message_user(request, f"Transferencia {transferencia.id} marcada como RECHAZADA.", level='success')
                except ValueError as e:
                    self.message_user(request, f"Error al rechazar transferencia {transferencia.id}: {e}", level='error')
                except Exception as e:
                    self.message_user(request, f"Error inesperado al rechazar transferencia {transferencia.id}: {e}", level='error')
            else:
                self.message_user(request, f"Transferencia {transferencia.id} no puede ser rechazada. Estado actual: {transferencia.estado}.", level='warning')
    marcar_como_rechazado.short_description = "Marcar seleccionados como Rechazados"

