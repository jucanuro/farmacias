from django.db import models


class WhatsAppLeadEvent(models.Model):
    CONTACT_TYPE_CHOICES = [
        ("soporte", "Soporte"),
        ("ventas", "Ventas"),
    ]

    contact_type = models.CharField(max_length=20, choices=CONTACT_TYPE_CHOICES)
    phone_number = models.CharField(max_length=20)
    message = models.TextField(blank=True)
    source_page = models.CharField(max_length=150, blank=True)
    user_agent = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    referrer = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Evento WhatsApp IA"
        verbose_name_plural = "Eventos WhatsApp IA"

    def __str__(self):
        return f"{self.contact_type} - {self.phone_number} - {self.created_at}"