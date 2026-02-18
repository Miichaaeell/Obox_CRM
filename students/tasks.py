from datetime import timedelta

from celery import shared_task
from decouple import config
from django.db import transaction
from django.db.models import Count
from django.utils import timezone
from core.settings import c, log_error, log_success

from students.models import History, MonthlyFee, StatusStudent, Student
from enterprise.models import Plan


@shared_task
def create_monthlyfee():
    students: list = (
        Student.objects.filter(status__status__iexact="ativo")
        .select_related("plan", "status")
        .prefetch_related("monthly_fees")
    )
    # TODO: Refatorar a criação da mensalidade utilizando a quantidade de meses trago pela relação do plano
    now = timezone.localdate()
    month, year = now.month, now.year
    current_month_index = (year * 12) + month
    trimestral_plan = Plan.objects.filter(name__icontains="trimestral").first()
    create_to_monthlyfee: list = []
    for student in students:
        try:
            if student.plan == trimestral_plan:
                last_fee = student.monthly_fees.order_by("-created_at").first()
                if last_fee:
                    last_fee_month_index = (
                        last_fee.created_at.year * 12
                    ) + last_fee.created_at.month
                    if (current_month_index - last_fee_month_index) <= 2:
                        continue
            create_to_monthlyfee.append(
                MonthlyFee(
                    student=student,
                    student_name=student.name,
                    amount=student.plan.price,
                    due_date=f"{year}-{month}-{student.due_date}",
                    reference_month=f"{month}/{year}",
                    plan=student.plan,
                )
            )
        except Exception as e:
            log_error("Erro ao criar lista de mensalidades")
            c.log(e, style="bold red", justify="justify")
            return {"message": f"Erro ao processar o arquivo {e}", "status_code": "422"}
    if create_to_monthlyfee:
        try:
            MonthlyFee.objects.bulk_create(create_to_monthlyfee)
            log_success(
                f"Criadas {len(create_to_monthlyfee)} mensalidades com sucesso!"
            )
            return f"Criadas {len(create_to_monthlyfee)} mensalidades."
        except Exception as e:
            log_error("Erro ao criar mensalidades")
            c.log(e, style="bold red", justify="justify")
            return {"message": f"Erro ao criar mensalidades: {e}", "status_code": "422"}
    else:
        log_success("Nenhum aluno ativo encontrado, nada criado.")
        return "Nenhum aluno ativo encontrado, nada criado."


@shared_task
def deactivate_overdue_students(days_overdue: int | None = None):
    if days_overdue is None:
        days_overdue = config("STUDENT_OVERDUE_DAYS", default=30, cast=int)
    if days_overdue < 0:
        log_error("Dias de atraso inválido para inativação.")
        return {"message": "Dias de atraso inválido.", "status_code": "422"}

    cutoff = timezone.localdate() - timedelta(days=days_overdue)

    overdue_student_ids = list(
        MonthlyFee.objects.filter(
            paid=False,
            due_date__lte=cutoff,
            student__status__status__iexact="Ativo",
        )
        .values_list("student_id", flat=True)
        .distinct()
    )

    if not overdue_student_ids:
        log_success("Nenhum aluno com atraso acima do limite.")
        return "Nenhum aluno com atraso acima do limite."

    inactive_status = StatusStudent.objects.filter(status__iexact="Inativo").first()
    if not inactive_status:
        log_error("Status 'Inativo' não encontrado.")
        return {"message": "Status 'Inativo' não encontrado.", "status_code": "422"}

    description = f"Aluno inativado automaticamente após {days_overdue} dias de atraso."

    with transaction.atomic():
        unpaid_counts = list(
            MonthlyFee.objects.filter(student_id__in=overdue_student_ids, paid=False)
            .values("student_id")
            .annotate(total=Count("id"))
        )
        deleted_total, _ = MonthlyFee.objects.filter(
            student_id__in=overdue_student_ids, paid=False
        ).delete()
        Student.objects.filter(id__in=overdue_student_ids).update(
            status=inactive_status, observation=description
        )
        History.objects.bulk_create(
            [
                History(
                    student_id=item["student_id"],
                    status=inactive_status,
                    description=f"{item['total']} Mensalidades excluídas. {description}",
                )
                for item in unpaid_counts
            ]
        )

    log_success(
        f"Inativados {len(overdue_student_ids)} alunos e excluídas {deleted_total} mensalidades."
    )
    return {
        "inactivated_students": len(overdue_student_ids),
        "deleted_fees": deleted_total,
    }
