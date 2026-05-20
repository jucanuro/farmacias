from django.urls import path
from . import views

app_name = 'ia_assistant'

urlpatterns = [
    path('', views.ai_chat_view, name='chat'),
    path('api/chat/', views.ai_chat_api_view, name='api_chat'),
    path('whatsapp/<str:contact_type>/', views.whatsapp_redirect_view, name='whatsapp_redirect'),
]