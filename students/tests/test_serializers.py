from decimal import Decimal

from django.test import TestCase

from enterprise.models import Plan
from students.models import MonthlyFee, StatusStudent, Student, History
from students.serializers import StudentSerializer


class StudentSerializerTests(TestCase):
    def setUp(self):
        self.status_active = StatusStudent.objects.create(status="Ativo")
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
            status=self.status_active,
            observation="Test",
            plan=self.plan,
        )
        MonthlyFee.objects.create(
            student=self.student,
            student_name=self.student.name,
            amount=Decimal("100.00"),
            due_date="2025-01-01",
            reference_month="01/2025",
            paid=False,
            plan=self.plan,
        )

    def test_update_status_deletes_unpaid_fees_and_records_history(self):
        serializer = StudentSerializer(
            instance=self.student,
            data={"status": self.status_inactive.id},
            partial=True,
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()
        self.assertEqual(
            MonthlyFee.objects.filter(student=self.student, paid=False).count(),
            0,
        )
        self.assertTrue(
            History.objects.filter(
                student=self.student, description__icontains="Mensalidades"
            ).exists()
        )
