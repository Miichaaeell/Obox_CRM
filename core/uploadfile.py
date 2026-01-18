from datetime import datetime

import pandas as pd
from rich.console import Console

from enterprise.models import Plan
from students.models import MonthlyFee, StatusStudent, Student

c = Console()


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
        return {"message": "Formato de arquivo inválido", "status_code": "400"}
    match ext:
        case "csv":
            df = pd.read_csv(file)
        case "xlsx":
            df = pd.read_excel(file)

    df.columns = df.columns.str.lower().str.strip()
    try:
        data = (
            df[
                [
                    "nome",
                    "contrato",
                    "cpf",
                    "status",
                    "data_de_nascimento",
                    "data_de_cadastro",
                ]
            ]
            .drop_duplicates()
            .dropna()
        )
        data["cpf"] = data["cpf"].apply(format_cpf)
        data["data_de_nascimento"], data["due_date"] = (
            data["data_de_nascimento"].dt.date,
            data["data_de_cadastro"],
        )
    except Exception as e:
        return {"message": f"Erro ao processar o arquivo {e}", "status_code": "422"}
    # try:
    #     Student.objects.all().delete()
    #     MonthlyFee.objects.all().delete()
    # except Exception as e:
    #     c.log(
    #         f"Erro ao limpar tabela de alunos e mensalidades: {e}",
    #         style="bold red",
    #         justify="center",
    #     )

    try:
        create_student = [
            Student(
                name=row.nome,
                cpf_cnpj=row.cpf,
                date_of_birth=row.data_de_nascimento,
                status=StatusStudent.objects.get(
                    status__iexact=str(row.status)
                ),
                observation=f"Importado via arquivo em {datetime.now().date()}",
                due_date=row.due_date if row.due_date else datetime.now().day(),
                plan=Plan.objects.get(name_plan__iexact=row.contrato),
            )
            for row in data.itertuples(index=False)
        ]

    except Exception as e:
        c.log(f"Erro ao criar lista de alunos {e}", style="bold red", justify="center")
        return {"message": f"Erro ao processar o arquivo {e}", "status_code": "422"}
    Student.objects.bulk_create(create_student)
    try:
        create_monthly_fee = [
            MonthlyFee(
                student=studant_instance,
                student_name=studant_instance.name,
                due_date=studant_instance.created_at,
                reference_month=datetime.now().month - 1,
                amount=studant_instance.plan.price,
                plan=studant_instance.plan,
            )
            for studant_instance in create_student
        ]
    except Exception as e:
        c.log(
            f"Erro ao criar lista de mensalidades: {e}",
            style="bold red",
            justify="center",
        )
    MonthlyFee.objects.bulk_create(create_monthly_fee)
    return {"message": f"Arquivo {file} carregado com sucesso!", "status_code": "201"}
