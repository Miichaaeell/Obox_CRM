from datetime import datetime

from celery import shared_task

from students.models import MonthlyFee, Student


@shared_task
def create_monthlyfee():
    students: list = Student.objects.filter(
        status__status__iexact="ativo"
    ).select_related("plan", "status")

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
        return f"Criadas {len(create_to_monthlyfee)} mensalidades."
    else:
        return "Nenhum aluno ativo encontrado, nada criado."
