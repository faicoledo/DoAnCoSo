"""
Custom middleware for LMS
"""


class XFrameOptionsExemptMiddleware:
    """
    Middleware để bỏ X-Frame-Options header cho media files
    Cho phép iframe hiển thị PDF và các file khác từ frontend
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Bỏ X-Frame-Options cho media files để iframe có thể hiển thị
        if request.path.startswith('/media/'):
            response.xframe_options_exempt = True
            if 'X-Frame-Options' in response:
                del response['X-Frame-Options']
        
        return response

