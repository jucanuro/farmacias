from django.shortcuts import redirect
from django.urls import reverse

class OnboardingSaaSMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            return self.get_response(request)

        if request.user.is_superuser:
            return self.get_response(request)
        
        urls_permitidas = [
            reverse('core:farmacia_create'),
            reverse('core:logout'),
        ]

        if not request.user.farmacia:
            if request.path not in urls_permitidas:
                return redirect('core:farmacia_create')

        response = self.get_response(request)
        return response