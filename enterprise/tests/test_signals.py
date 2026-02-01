from datetime import date
from decimal import Decimal

from django.test import TestCase

from enterprise.models import Bill, PaymentMethod, StatusBill


class EnterpriseSignalsTests(TestCase):
    def setUp(self):
        self.status_pending = StatusBill.objects.create(status="PENDENTE")
        self.status_auto = StatusBill.objects.create(status="automatico")
        self.method_cash = PaymentMethod.objects.create(method="Dinheiro")
        self.method_auto = PaymentMethod.objects.create(method="deb. automatico")

    def test_bill_created_with_automatic_method_sets_payment(self):
        bill = Bill.objects.create(
            description="Conta",
            value=Decimal("80.00"),
            due_date=date.today(),
            status=self.status_pending,
            payment_method=self.method_auto,
        )
        bill.refresh_from_db()
        self.assertEqual(bill.status, self.status_auto)
        self.assertEqual(bill.date_payment, bill.due_date)

    def test_bill_change_to_automatic_updates_fields(self):
        bill = Bill.objects.create(
            description="Conta",
            value=Decimal("80.00"),
            due_date=date.today(),
            status=self.status_pending,
            payment_method=self.method_cash,
        )
        bill.payment_method = self.method_auto
        bill.save()
        bill.refresh_from_db()
        self.assertEqual(bill.status, self.status_auto)
        self.assertEqual(bill.date_payment, bill.due_date)


class EnterpriseSignalsMissingStatusTests(TestCase):
    def setUp(self):
        self.status_pending = StatusBill.objects.create(status="PENDENTE")
        self.method_auto = PaymentMethod.objects.create(method="deb. automatico")

    def test_bill_automatic_without_status_raises(self):
        with self.assertRaises(Exception):
            Bill.objects.create(
                description="Conta",
                value=Decimal("80.00"),
                due_date=date.today(),
                status=self.status_pending,
                payment_method=self.method_auto,
            )
