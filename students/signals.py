from datetime import datetime

from django.db.models.signals import post_save
from django.dispatch import receiver

from students.models import History, MonthlyFee, Student


@receiver(post_save, sender=Student)
def student_history(sender, instance, created, **kwargs):
    month, year = datetime.now().month, datetime.now().year
    if created:
        pass
    else:
        try:
            status_history = History.objects.filter(
                student=instance).order_by('-created_at').first()
            if instance.status != status_history.status:
                if instance.status.status.lower() == 'ativo':
                    MonthlyFee.objects.create(
                        student=instance,
                        amount=instance.plan.price,
                        due_date=f'{year}-{month}-{instance.due_date}',
                        reference_month=f"{month}/{year}"
                    )
        except:
            print('Nao foi encontrado historico')
    History.objects.create(
        student=instance, status=instance.status, description=instance.observation)
