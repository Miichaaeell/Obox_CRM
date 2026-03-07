from services.callmebot import callmebot
from os import getenv
from core.settings import c


class ExceptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exc) -> None:
        c.log("Enviando erro pelo whatsapp")
        bot = callmebot()
        bot.__call__(
            number="5519999894514", message=str(exc), api_key=getenv("API_KEY_MI")
        )
        bot.__call__(
            number="5519997751263", message=str(exc), api_key=getenv("API_KEY_MA")
        )
        return None
