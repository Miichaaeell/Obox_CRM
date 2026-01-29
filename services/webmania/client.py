import requests


class WebmaniaClient:
    def __init__(self, bearer_token: str, ambient: int = 2):
        self.__bearer_token = bearer_token
        self.__base_url = "https://api.webmaniabr.com/"
        self.__ambient = ambient  # 1 - Produção / 2 - Homologação
        self.__headers = {
            "Authorization": f"Bearer {self.__bearer_token}",
            "Content-Type": "application/json",
        }

    def send_nfs(self, data: dict):
        url = f"{self.__base_url}2/nfse/emissao"
        payload = {"ambiente": self.__ambient, "rps": [data]}
        response = requests.post(url, json=payload, headers=self.__headers)
        return response.json()

    def cancel_nfs(self, uuid_nfs: str, motivo: str):
        url = f"{self.__base_url}2/nfse/cancelar/{uuid_nfs}/"
        # 1 - Erro na emissão / 2 - Serviço não prestado / 4 - Duplicidade da nota
        payload = {"motivo": motivo}
        response = requests.put(url, json=payload, headers=self.__headers)
        return response.json()

    def get_nfs(self, uuid_nfs: str):
        url = f"{self.__base_url}2/nfse/consulta/{uuid_nfs}/"
        response = requests.get(url, headers=self.__headers)
        return response.json()

    def get_pdf_nfs(self, uuid_nfs: str, folder: str):
        pdf = requests.get(
            url=f"https://api.webmaniabr.com/nfse/{uuid_nfs}", headers=self.__headers
        )
        with open(f"{folder}/nfs_{uuid_nfs}.pdf", "wb") as file:
            file.write(pdf.content)

    def get_xml_nfs(self, uuid_nfs: str, folder: str):
        xml = requests.get(
            url=f"http://api.webmaniabr.com/xmlnfse/{uuid_nfs}", headers=self.__headers
        )
        with open(f"{folder}/nfs_{uuid_nfs}.xml", "wb") as file:
            file.write(xml.content)
