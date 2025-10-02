from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import Bill, StatusBill, PaymentMethod


@receiver(post_save, sender=Bill)
def verify_payment_method(sender, instance, created, **Kwargs):
    if created:
        method_automatico = PaymentMethod.objects.filter(
            method__icontains='automatico').first()
        if instance.payment_method == method_automatico:
            status_automatico = StatusBill.objects.filter(
                status__icontains='AUTOMÁTICO').first()
            instance.date_payment = instance.due_date
            instance.status = status_automatico
            instance.save()
        else:
            instance.total_value = None
            instance.save()


@receiver(pre_save, sender=Bill)
def verify_change_method(sender, instance, **kwargs):
    bill = Bill.objects.get(id=instance.id)
    method_automatic = PaymentMethod.objects.filter(
        method__icontains='automatico').first()
    status_automatic = StatusBill.objects.filter(
        status__icontains='AUTOMÁTICO').first()
    status_pendent = StatusBill.objects.filter(
        status__icontains='pendente').first()
    if bill.payment_method != instance.payment_method:
        if instance.payment_method == method_automatic:
            instance.date_payment = instance.due_date
            instance.total_value = instance.value
            instance.status = status_automatic
        else:
            instance.date_payment = None
            instance.total_value = None
            instance.status = status_pendent

    elif bill.status != instance.status:
        if instance.payment_method == method_automatic:
            instance.date_payment = bill.due_date
            instance.total_value = bill.value
            instance.status = bill.status
