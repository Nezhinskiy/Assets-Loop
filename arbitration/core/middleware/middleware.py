from django.http import HttpResponseForbidden

from arbitration.settings import ALLOWED_HOSTS


class RestrictIPMiddleware:
    def __init__(self, get_response=None, allowed_ips=ALLOWED_HOSTS):
        self.get_response = get_response
        self.allowed_ips = allowed_ips or []

    def __call__(self, request):
        ip_address = request.META.get('HTTP_X_FORWARDED_FOR',
                                      request.META.get('REMOTE_ADDR'))
        if ip_address not in self.allowed_ips and '*' not in self.allowed_ips:
            return HttpResponseForbidden('Access denied')
        return self.get_response(request)


class RestrictIPMiddlewareForAPIData(RestrictIPMiddleware):
    def __init__(self, get_response=None, allowed_ips=ALLOWED_HOSTS):
        super().__init__(get_response, allowed_ips)
        self.get_response = get_response
        self.allowed_ips = ALLOWED_HOSTS

    def __call__(self, request):
        if request.path.startswith('/data/'):
            return super().__call__(request)
        return self.get_response(request)
