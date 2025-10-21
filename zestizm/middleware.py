import re
from django.http import Http404

class BlockWPExploitAttemptsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.wp_patterns = re.compile(r'(wp-admin|wp-content|wp-includes|wp-login|\.php$)')

    def __call__(self, request):
        path = request.path_info
        if self.wp_patterns.search(path):
            raise Http404()
        
        response = self.get_response(request)
        return response
    