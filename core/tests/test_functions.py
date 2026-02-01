from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from core.functions import get_context_homeview, get_dashboard_context
from enterprise.models import Bill, Installments, PaymentMethod, StatusBill
from students.models import MonthlyFee, Payment, StatusStudent, Student
from enterprise.models import Plan


class CoreFunctionsTests(TestCase):
    def setUp(self):
        self.status_active = StatusStudent.objects.create(status="Ativo")
        self.status_inactive = StatusStudent.objects.create(status="Inativo")
        self.plan = Plan.objects.create(
            name_plan="Plan A",
            description="Test",
            price=Decimal("100.00"),
            duration_months=12,
        )
        self.student_active = Student.objects.create(
            name="Student A",
            cpf_cnpj="12345678901",
            status=self.status_active,
            observation="Test",
            plan=self.plan,
        )
        self.student_inactive = Student.objects.create(
            name="Student B",
            cpf_cnpj="12345678902",
            status=self.status_inactive,
            observation="Test",
            plan=self.plan,
        )
        self.payment_method = PaymentMethod.objects.create(
            method="Pix",
            applies_to="students",
        )
        Installments.objects.create(quantity_installments=1)

    def test_get_context_homeview(self):
        today = timezone.localdate()
        MonthlyFee.objects.create(
            student=self.student_active,
            student_name=self.student_active.name,
            amount=Decimal("100.00"),
            due_date=today + timedelta(days=1),
            reference_month=f"{today.month}/{today.year}",
            plan=self.plan,
        )
        status_bill = StatusBill.objects.create(status="Pendente")
        Bill.objects.create(
            description="Bill",
            value=Decimal("50.00"),
            due_date=today,
            status=status_bill,
            payment_method=self.payment_method,
        )
        context = get_context_homeview()
        self.assertEqual(context["actives_total"], 1)
        self.assertIn("monthly_fees_due_total", context)
        self.assertIn("calendar_events", context)
        self.assertIn("accounts_url", context)

    def test_get_dashboard_context(self):
        today = timezone.localdate()
        MonthlyFee.objects.create(
            student=self.student_active,
            student_name=self.student_active.name,
            amount=Decimal("120.00"),
            due_date=today,
            reference_month=f"{today.month}/{today.year}",
            paid=True,
            plan=self.plan,
        )
        MonthlyFee.objects.create(
            student=self.student_inactive,
            student_name=self.student_inactive.name,
            amount=Decimal("80.00"),
            due_date=today + timedelta(days=3),
            reference_month=f"{today.month}/{today.year}",
            paid=False,
            plan=self.plan,
        )
        MonthlyFee.objects.create(
            student=self.student_inactive,
            student_name=self.student_inactive.name,
            amount=Decimal("60.00"),
            due_date=today - timedelta(days=2),
            reference_month=f"{today.month}/{today.year}",
            paid=False,
            plan=self.plan,
        )
        Payment.objects.create(
            montlhyfee=MonthlyFee.objects.first(),
            payment_method="pix",
            value=Decimal("120.00"),
            quantity_installments=1,
        )
        Payment.objects.create(
            montlhyfee=MonthlyFee.objects.first(),
            payment_method="credito",
            value=Decimal("50.00"),
            quantity_installments=1,
        )
        status_bill = StatusBill.objects.create(status="Pendente")
        Bill.objects.create(
            description="Bill 1",
            value=Decimal("30.00"),
            due_date=today,
            status=status_bill,
            payment_method=self.payment_method,
        )
        Bill.objects.create(
            description="Bill 2",
            value=Decimal("40.00"),
            due_date=today - timedelta(days=1),
            status=status_bill,
            payment_method=self.payment_method,
            date_payment=today,
        )
        context = get_dashboard_context()
        self.assertIn("students_summary", context)
        self.assertIn("monthly_fee_values", context)
        self.assertIn("bills_summary", context)
        self.assertIn("payment_method_stats", context)
        self.assertIn("nfse_summary", context)
