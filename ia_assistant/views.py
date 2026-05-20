import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .services import QhaliAIService
from urllib.parse import quote
from .models import WhatsAppLeadEvent


def ai_chat_view(request):
    return render(request, 'ia_assistant_templates/ai_chat.html')


@require_POST
def ai_chat_api_view(request):
    try:
        data = json.loads(request.body)
        message = data.get("message", "").strip()

        if not message:
            return JsonResponse({
                "success": False,
                "message": "Debes escribir una pregunta."
            }, status=400)

        service = QhaliAIService()
        response = service.get_response(message)

        return JsonResponse({
            "success": True,
            "response": response
        })

    except json.JSONDecodeError:
        return JsonResponse({
            "success": False,
            "message": "Formato JSON inválido."
        }, status=400)

    except Exception as e:
        return JsonResponse({
            "success": False,
            "message": f"Error inesperado: {str(e)}"
        }, status=500)
        

def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def whatsapp_redirect_view(request, contact_type):
    contacts = {
        "soporte": {
            "phone": "51916393838",
            "label": "soporte",
            "message": "Hola, necesito soporte sobre Qhalisys+.",
        },
        "ventas": {
            "phone": "51944351698",
            "label": "ventas",
            "message": "Hola, quiero información sobre Qhalisys+ para mi farmacia.",
        },
    }

    contact = contacts.get(contact_type)

    if not contact:
        return redirect("/")

    source_page = request.GET.get("source", "landing")

    WhatsAppLeadEvent.objects.create(
        contact_type=contact["label"],
        phone_number=contact["phone"],
        message=contact["message"],
        source_page=source_page,
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
        ip_address=get_client_ip(request),
        referrer=request.META.get("HTTP_REFERER", ""),
    )

    whatsapp_url = f"https://wa.me/{contact['phone']}?text={quote(contact['message'])}"

    return redirect(whatsapp_url)

