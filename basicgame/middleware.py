class NoCachingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response["Cache-Control"] = "no-cache, max-age=0, must-revalidate, no-store"
        response["Cache-Control"] = "post-check=0, pre-check=0, false"
        response["Pragma"] = "no-cache"
        response["Expires"] = 0
        return response
