from datetime import datetime

import pandas as pd
from core.settings import log_error, log_success, c
from enterprise.models import Plan
from students.models import MonthlyFee, StatusStudent, Student


def format_cpf(cpf: str) -> str:
    # remove tudo que não for número
    cpf = "".join(filter(str.isdigit, str(cpf)))
    # garante 11 dígitos
    cpf = cpf.zfill(11)
    # aplica a máscara
    return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"


def upload_file(file) -> dict:
    ext: str = file.name.split(".")[-1].lower()
    if ext not in ["xlsx", "csv"]:
        log_error(f"Formato de arquivo inválido: {ext} não é permitido.")
        return {"message": "Formato de arquivo inválido", "status_code": "400"}
    match ext:
        case "csv":
            df = pd.read_csv(file)
        case "xlsx":
            df = pd.read_excel(file)

    df.columns = df.columns.str.lower().str.strip().str.replace(" ", "")
    try:
        data = (
            df[
                [
                    "nome",
                    "contrato",
                    "cpf",
                    "status",
                    "datadenascimento",
                    "diadopagamento",
                ]
            ]
            .drop_duplicates()
            .dropna()
        )
        data["cpf"] = data["cpf"].apply(format_cpf)
        data["data_de_nascimento"], data["due_date"] = (
            data["datadenascimento"].dt.date,
            data["diadopagamento"],
        )
    except Exception as e:
        log_error("Erro ao processar o arquivo")
        c.log(e, style="bold red", justify="justify")
        return {"message": f"Erro ao processar o arquivo {e}", "status_code": "422"}

    # try:
    #     from enterprise.models import NFSe, PaymentMethod, Bill
    #     from students.models import Frequency, Payment

    #     Bill.objects.all().delete()
    #     PaymentMethod.objects.all().delete()
    #     NFSe.objects.all().delete()
    #     Frequency.objects.all().delete()
    #     Payment.objects.all().delete()
    #     MonthlyFee.objects.all().delete()
    #     Student.objects.all().delete()

    # except Exception as e:
    #     c.log(
    #         f"Erro ao limpar tabela de alunos e mensalidades: {e}",
    #         style="bold red",
    #         justify="center",
    #     )
    #     return {"message": f"Erro ao limpar tabelas: {e}", "status_code": "422"}

    try:
        create_student = [
            Student(
                name=row.nome,
                cpf_cnpj=row.cpf,
                date_of_birth=row.data_de_nascimento,
                status=StatusStudent.objects.get(status__iexact=str(row.status)),
                observation=f"Importado via arquivo em {datetime.now().date()}",
                due_date=row.due_date if row.due_date else datetime.now().day(),
                plan=Plan.objects.get(name_plan__iexact=row.contrato),
            )
            for row in data.itertuples(index=False)
        ]

    except Exception as e:
        log_error("Erro ao criar lista de alunos")
        c.log(e, style="bold red", justify="justify")
        return {"message": f"Erro ao processar o arquivo {e}", "status_code": "422"}
    try:
        create_monthly_fee = [
            MonthlyFee(
                student=studant_instance,
                student_name=studant_instance.name,
                due_date=datetime.now().date().replace(day=studant_instance.due_date),
                reference_month=datetime.now().month - 1,
                amount=studant_instance.plan.price,
                plan=studant_instance.plan,
            )
            for studant_instance in create_student
        ]
    except Exception as e:
        log_error("Erro ao criar lista de mensalidades")
        c.log(e, style="bold red", justify="justify")
        return {"message": f"Erro ao processar o arquivo {e}", "status_code": "422"}
    try:
        Student.objects.bulk_create(create_student)
        MonthlyFee.objects.bulk_create(create_monthly_fee)
    except Exception as e:
        log_error("Erro ao criar alunos e mensalidades")
        c.log(e, style="bold red", justify="justify")
        return {
            "message": f"Erro ao criar alunos e mensalidades: {e}",
            "status_code": "422",
        }
    log_success(f"Arquivo {file} carregado com sucesso!")
    c.log(
        f"Total de {len(create_student)} alunos e {len(create_monthly_fee)} mensalidades cadastrados com sucesso!",
        style="bold green",
        justify="justify",
    )
    return {"message": f"Arquivo {file} carregado com sucesso!", "status_code": "201"}
