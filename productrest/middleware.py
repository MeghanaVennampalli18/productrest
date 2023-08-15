from django.http import JsonResponse
from django.urls import resolve
from django.urls.exceptions import Resolver404

class InvalidRouteMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            resolve(request.path_info)
        except Resolver404:
            return JsonResponse({'error': 'Invalid route'}, status=404)
        
        return self.get_response(request)