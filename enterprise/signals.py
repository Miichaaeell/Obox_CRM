from django.db.models import Q
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from rich.console import Console

from enterprise.models import Bill, PaymentMethod, StatusBill

c = Console()


@receiver(post_save, sender=Bill)
def verify_payment_method(sender, instance, created, **Kwargs):
    if created:
        method_automatico = PaymentMethod.objects.filter(
            Q(method__icontains="automatico") | Q(method__icontains="automático")
        ).first()
        if instance.payment_method == method_automatico:
            status_automatic = StatusBill.objects.filter(
                Q(status__icontains="automatico") | Q(status__icontains="automático")
            ).first()
            instance.date_payment = instance.due_date
            instance.status = status_automatic
            instance.save()
        else:
            instance.total_value = None
            instance.save()


@receiver(pre_save, sender=Bill)
def verify_change_method(sender, instance, **kwargs):
    bill = Bill.objects.filter(id=instance.id).first()
    if bill:
        try:
            method_automatic = PaymentMethod.objects.filter(
                Q(method__icontains="automatico") | Q(method__icontains="automático")
            ).first()
            status_automatic = StatusBill.objects.filter(
                Q(status__icontains="automatico") | Q(status__icontains="automático")
            ).first()
            if bill.payment_method != instance.payment_method:
                if instance.payment_method == method_automatic:
                    instance.date_payment = instance.due_date
                    instance.total_value = instance.value
                    instance.status = status_automatic
                else:
                    status_pendent = StatusBill.objects.filter(
                        status__icontains="PENDENTE"
                    ).first()
                    instance.date_payment = None
                    instance.total_value = None
                    instance.status = status_pendent

            elif bill.status != instance.status:
                if instance.payment_method == method_automatic:
                    instance.date_payment = bill.due_date
                    instance.total_value = bill.value
                    instance.status = status_automatic
        except Exception as e:
            c.log(f"Pré save {e}", style="bold red", justify="center")
