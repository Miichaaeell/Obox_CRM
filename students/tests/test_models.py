from datetime import date
from decimal import Decimal

from django.db import IntegrityError
from django.db.transaction import TransactionManagementError
from django.test import TestCase
from django.utils import timezone

from enterprise.models import Cashier, Plan
from students.models import (
    Frequency,
    History,
    MonthlyFee,
    Payment,
    StatusStudent,
    Student,
)


class StudentModelsTests(TestCase):
    def setUp(self):
        self.status = StatusStudent.objects.create(status="Ativo")
        self.status_inactive = StatusStudent.objects.create(status="Inativo")
        self.plan = Plan.objects.create(
            name_plan="Plan A",
            description="Test",
            price=Decimal("100.00"),
            duration_months=12,
        )
        self.student = Student.objects.create(
            name="Student A",
            cpf_cnpj="12345678901",
            status=self.status,
            observation="Test",
            plan=self.plan,
        )

    def test_status_str(self):
        self.assertEqual(str(self.status), "Ativo")

    def test_student_str(self):
        self.assertEqual(str(self.student), "Student A")

    def test_frequency_str(self):
        freq = Frequency.objects.create(student=self.student)
        self.assertIn(self.student.name, str(freq))

    def test_frequency_unique(self):
        today = timezone.localdate()
        Frequency.objects.create(student=self.student, attendance_date=today)
        with self.assertRaises(IntegrityError):
            Frequency.objects.create(student=self.student, attendance_date=today)

    def test_history_str(self):
        history = History.objects.create(
            student=self.student, status=self.status, description="Test"
        )
        self.assertIn(self.student.name, str(history))

    def test_monthly_fee_str(self):
        fee = MonthlyFee.objects.create(
            student=self.student,
            student_name=self.student.name,
            amount=Decimal("100.00"),
            due_date=date.today(),
            reference_month="01/2025",
            paid=False,
            plan=self.plan,
        )
        self.assertIn("Pendente", str(fee))

    def test_payment_str(self):
        fee = MonthlyFee.objects.create(
            student=self.student,
            student_name=self.student.name,
            amount=Decimal("100.00"),
            due_date=date.today(),
            reference_month="01/2025",
            paid=False,
            plan=self.plan,
        )
        cashier = Cashier.objects.create(status="open")
        payment = Payment.objects.create(
            montlhyfee=fee,
            payment_method="pix",
            value=Decimal("100.00"),
            quantity_installments=1,
            cashier=cashier,
        )
        self.assertIn("R$ 100.00", str(payment))

    def test_student_without_observation_raises(self):
        with self.assertRaises(IntegrityError):
            Student.objects.create(
                name="Student B",
                cpf_cnpj="12345678902",
                status=self.status,
                observation=None,
                plan=self.plan,
            )

    def test_activate_without_due_date_raises(self):
        student = Student.objects.create(
            name="Student C",
            cpf_cnpj="12345678903",
            status=self.status_inactive,
            observation="Test",
            due_date=None,
            plan=self.plan,
        )
        student.status = self.status
        with self.assertRaises(TransactionManagementError):
            student.save()
