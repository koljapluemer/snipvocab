import re
from django.conf import settings
from django.http import JsonResponse


class APIKeyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the path matches any of the exempt patterns
        path = request.path_info.lstrip('/')
        for exempt_pattern in settings.API_KEY_EXEMPT_PATHS:
            if re.match(exempt_pattern, path):
                return self.get_response(request)

        # Check if the path requires API key
        requires_api_key = False
        for required_pattern in settings.API_KEY_REQUIRED_PATHS:
            if re.match(required_pattern, path):
                requires_api_key = True
                break

        if requires_api_key:
            api_key = request.headers.get(settings.API_KEY_HEADER)
            if not api_key or api_key != settings.API_KEY:
                return JsonResponse(
                    {"error": "Invalid or missing API key"},
                    status=403
                )

        return self.get_response(request) 