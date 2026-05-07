from social_core.exceptions import AuthForbidden
from django.shortcuts import redirect

class SocialAuthExceptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        if isinstance(exception, AuthForbidden):
            return redirect('/login/?error=1')
        return None
