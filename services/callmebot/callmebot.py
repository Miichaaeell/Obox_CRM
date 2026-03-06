from requests import post
from core.settings import c, log_error


class callmebot:
    def __init__(self):
        self.__base_url = "https://api.callmebot.com//whatsapp.php?phone={number}&text={message}&apikey={api_key}"

    def __call__(self, number: str, message: str, api_key: str) -> None:
        try:
            post(
                self.__base_url.format(
                    number=number,
                    message=message,
                )
            )
        except Exception as e:
            log_error("Erro ao enviar mensagem pelo whatsapp")
            c.log(e)
