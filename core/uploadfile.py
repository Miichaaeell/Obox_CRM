import pandas as pd

from enterprise.models import Plan
from students.models import StatusStudent, Student


def format_cpf(cpf):
    # remove tudo que não for número
    cpf = ''.join(filter(str.isdigit, str(cpf)))
    # garante 11 dígitos
    cpf = cpf.zfill(11)
    # aplica a máscara
    return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"


def upload_file(file):
    ext = file.name.split('.')[-1].lower()
    if ext not in ['xlsx', 'csv']:
        return {
            "message": f'Formato de arquivo inválido',
            "status_code": '400'
        }
    match ext:
        case 'csv':
            df = pd.read_csv(file)
        case 'xlsx':
            df = pd.read_excel(file)

    df.columns = df.columns.str.lower().str.strip()
    try:
        data = df[['nome', 'contrato', 'telefone', 'cpf',
                   'status', 'data_de_nascimento', 'data_de_cadastro']].drop_duplicates().dropna()
        data[f'cpf'] = data['cpf'].apply(format_cpf)
        data['data_de_nascimento'], data['data_de_cadastro'], data['due_date'] = data[
            'data_de_nascimento'].dt.date, data['data_de_cadastro'].dt.date, data['data_de_cadastro'].dt.day
    except Exception as e:
        return {
            "message": f'Erro ao processar o arquivo {e}',
            "status_code": '422'
        }

    try:
        create_student = [
            Student(
                name=row.nome,
                cpf_cnpj=row.cpf,
                date_of_birth=row.data_de_nascimento,
                phone_number=row.telefone,
                status=StatusStudent.objects.filter(
                    status__iexact=str(row.status)).first(),
                observation='Trago da base de dados',
                due_date=row.due_date,
                plan=Plan.objects.get(name_plan__iexact=row.contrato),
                created_at=row.data_de_cadastro
            ) for row in data.itertuples(index=False)
        ]
        print(create_student)
    except Exception as e:
        print(f'Erro ao criar lista de alunos')
    Student.objects.bulk_create(create_student)
    return {
        "message": f'Arquivo {file} carregado com sucesso!',
        "status_code": '201'
    }
