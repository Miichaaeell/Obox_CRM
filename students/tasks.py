import logging
from datetime import datetime

from celery import shared_task

from students.models import MonthlyFee, Student


logger = logging.getLogger(__name__)

# Criar mensalidades


@shared_task
def create_monthlyfee():
    logger.warning("🚀 Iniciando task create_monthlyfee")

    students = Student.objects.filter(
        status__status__iexact='ativo').select_related('plan', 'status')
    logger.info(f"Encontrados {students.count()} alunos ativos")

    month, year = datetime.now().month, datetime.now().year
    create_to_monthlyfee = [
        MonthlyFee(
            student=student,
            student_name=student.name,
            amount=student.plan.price,
            due_date=f"{year}-{month}-{student.due_date}",
            reference_month=f"{month}/{year}",
            plan=student.plan,
        )
        for student in students
    ]

    if create_to_monthlyfee:
        MonthlyFee.objects.bulk_create(create_to_monthlyfee)
        logger.info(f"Criadas {len(create_to_monthlyfee)} mensalidades.")
    else:
        logger.info("Nenhum aluno ativo encontrado, nada criado.")

    logger.warning("✅ Finalizada task create_monthlyfee")
