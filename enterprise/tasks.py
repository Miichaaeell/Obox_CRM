from datetime import datetime
from dateutil.relativedelta import relativedelta

from celery import shared_task
from decouple import config
from rich.console import Console
from services.webmania.client import WebmaniaClient

from enterprise.models import Bill, StatusBill, Enterprise, NFSe
from students.models import Student

c = Console()


@shared_task
def create_recurring_bill() -> None:
    year, month = datetime.now().year, datetime.now().month
    today: str = datetime.now().date()
    first_day_this_month = today.replace(day=1)
    first_day_last_month = first_day_this_month - relativedelta(months=1)
    bills = Bill.objects.filter(
        appellant=True,
        due_date__lt=first_day_this_month,
        due_date__gte=first_day_last_month,
    )
    create_to_bill = []
    for bill in bills:
        if bill.payment_method.method.lower() == "deb. automatico":
            create_to_bill.append(
                Bill(
                    description=bill.description,
                    value=bill.value,
                    due_date=f"{year}-{month}-{bill.due_date.day}",
                    status=bill.status,
                    payment_method=bill.payment_method,
                    appellant=bill.appellant,
                    date_payment=bill.date_payment,
                    apply_discount=bill.apply_discount,
                    value_discount=bill.value_discount,
                    percent_discount=bill.percent_discount,
                    value_fine=bill.value_fine,
                    percent_fine=bill.percent_fine,
                    total_value=bill.total_value,
                )
            )
        else:
            status_pendente, _ = StatusBill.objects.get_or_create(
                status__icontains="pendente"
            )
            create_to_bill.append(
                Bill(
                    description=bill.description,
                    value=bill.value,
                    due_date=f"{year}-{month}-{bill.due_date.day}",
                    status=status_pendente,
                    payment_method=bill.payment_method,
                    appellant=bill.appellant,
                )
            )
    Bill.objects.bulk_create(create_to_bill)

    return f"Create {len(create_to_bill)} bills"


@shared_task
def send_NFS(data: dict) -> str:
    students: list[dict] = data["student"]
    description: str = data["description"]
    reference_month: str = data["reference_month"]
    bearer_token: str = config("WEBMANIA_BEARER_TOKEN")
    ambient: int = int(config("WEBMANIA_AMBIENT", 2))
    enterprise = Enterprise.objects.first()
    success, failed = [], []
    create_nfse: list = list()
    c.log(enterprise.service_code)

    client = WebmaniaClient(bearer_token=bearer_token, ambient=ambient)
    for student in students:
        try:
            data: dict = {
                "servico": {
                    "valor_servicos": f"{student['valor']}",
                    "discriminacao": f"{description}",
                    "iss_retido": 2 if not enterprise.iss_retained else 1,
                    "codigo_servico": f"{str(enterprise.service_code)}",
                    "codigo_nbs": f"{str(enterprise.service_code)}000",
                    "informacoes_complementares": enterprise.name,
                    "tributacao_iss": "1",
                    "impostos": {"iss": f"{enterprise.iss_aliquot}"},
                },
                "tomador": {
                    "cpf": f"{student['cpf']}",
                    "nome_completo": f"{student['name']}",
                },
            }
            if enterprise.iss_retained:
                data["servico"]["responsavel_retencao_iss"] = 1
            response: dict = client.send_nfs(data=data)
            if response.get("error"):
                c.log(response)
                failed.append(f"Erro ao emitir nota para {student['name']}")
            else:
                success.append(f"Nota emitida com sucesso para {student['name']}")
                try:
                    student_instance = Student.objects.filter(
                        name__icontains=student["name"]
                    ).first()
                    create_nfse.append(
                        NFSe(
                            student=student_instance,
                            issue_date=datetime.now().date(),
                            uuid_nfse=response.get("uuid"),
                            link_pdf=response.get("pdf_rps"),
                            link_xml=response.get("xml"),
                            reference_month=reference_month,
                        )
                    )
                except Exception as e:
                    c.log(
                        f"Erro ao criar NFSe: {e}", style="bold red", justify="center"
                    )

        except Exception as e:
            c.log(
                f"Erro ao emitir nota para {student['name']}: {e}",
                style="bold red",
                justify="center",
            )
            failed.append(f"Erro ao emitir nota para {student['name']}")
    NFSe.objects.bulk_create(create_nfse)
    return f"Total de {len(success)} notas emitidas e total de {len(failed)} notas falharam"
