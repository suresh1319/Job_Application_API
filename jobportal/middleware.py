import re
from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse
from django.http import JsonResponse
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed

class PublicAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.public_urls = [re.compile(url) for url in settings.PUBLIC_URLS]
        self.public_urls.extend([
            re.compile(r'^admin/login/$'),
            re.compile(r'^swagger/.*$'),
            re.compile(r'^redoc/.*$'),
            re.compile(r'^api/schema/.*$'),
            re.compile(r'^api/docs/.*$'),
            re.compile(r'^api/token/.*$'),  # Make sure token endpoints are public
        ])
        self.jwt_authenticator = JWTAuthentication()

    def __call__(self, request):
        path = request.path_info.lstrip('/')
        
        # Check if the current path is public
        if any(url.match(path) for url in self.public_urls):
            return self.get_response(request)
            
        # Special handling for static files and favicon
        if any(path.startswith(static) for static in ['swagger/', 'redoc/', 'static/', 'media/']) or path == 'favicon.ico':
            return self.get_response(request)
        
        # Handle JWT authentication for API requests
        if path.startswith('api/'):
            try:
                # Try to authenticate with JWT
                auth_header = request.META.get('HTTP_AUTHORIZATION', '')
                if auth_header.startswith('Bearer '):
                    # If we have a token, try to authenticate
                    try:
                        validated_token = self.jwt_authenticator.get_validated_token(auth_header.split(' ')[1])
                        request.user = self.jwt_authenticator.get_user(validated_token)
                        # is_authenticated is a property, don't set it directly
                        # The user is already authenticated by get_user()
                        return self.get_response(request)
                    except (InvalidToken, AuthenticationFailed):
                        pass
                
                # If we get here, authentication failed
                return JsonResponse(
                    {'detail': 'Authentication credentials were not provided or are invalid.'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            except Exception as e:
                return JsonResponse(
                    {'detail': 'Error processing authentication.', 'error': str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        # For non-API requests, use default authentication
        if not request.user.is_authenticated:
            return redirect(f"{reverse('admin:login')}?next={request.path}")
            
        return self.get_response(request)
