from decouple import config
from webmania_client import WebmaniaClient


client = WebmaniaClient(
    bearer_token=config('WEBMANIA_BEARER_TOKEN'),
    venv=config('WEBMANIA_VENV'),
)

payload =  {
      "servico": {
        "valor_servicos": "5.00",
        "discriminacao": f"Prestação de Serviço referente a ...",
        "iss_retido": "2",
        "código_servico": "0.00",
        "codigo_cnae": "0000000",
        "informacoes_complementares": "Complement"
      },
      "tomador": {
        "cpf": "000.000.000.00",
        "nome_completo": "Nome do tomador",
        "cidade": "Cidade do tomador",
        "uf": "SP",
      }
    }

response = client.send_nfs(data=payload)
print(response)
