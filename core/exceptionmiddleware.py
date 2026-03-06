from services.callmebot import callmebot


class ExceptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exc) -> None:
        bot = callmebot()
        bot.__call__(number="5519999894514", message=str(exc), api_key="7967268")
        bot.__call__(number="5519997751263", message=str(exc), api_key="5299160")
        return None
