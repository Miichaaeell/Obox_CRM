from datetime import datetime
from celery import shared_task

from enterprise.models import Bill


@shared_task
def create_recurring_bill():
    bills = Bill.objects.filter(appellant=True)
    year, month = datetime.now().year, datetime.now().month
    create_to_bill = []
    for bill in bills:
        if bill.payment_method.method.lower() == 'deb. automatico':
            create_to_bill.append(
                Bill(
                    description=bill.description,
                    value=bill.value,
                    due_date=f'{year}-{month}-{bill.due_date.day}',
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
                ))
        else:
            create_to_bill.append(
                Bill(
                    description=bill.description,
                    value=bill.value,
                    due_date=f'{year}-{month}-{bill.due_date.day}',
                    status=bill.status,
                    payment_method=bill.payment_method,
                    appellant=bill.appellant,
                ))
    Bill.objects.bulk_create(create_to_bill)
