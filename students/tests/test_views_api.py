from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from enterprise.models import Plan
from students.models import MonthlyFee, StatusStudent, Student


class StudentApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        User = get_user_model()
        self.user = User.objects.create_user(
            username="tester",
            password="strong-password-123",
        )
        self.client.force_authenticate(self.user)

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
            status=self.status_inactive,
            observation="Test",
            due_date=1,
            plan=self.plan,
        )

    def test_frequency_get_invalid_date(self):
        response = self.client.get(reverse("frequency_api"), {"date": "bad"})
        self.assertEqual(response.status_code, 400)

    def test_frequency_post_requires_student(self):
        response = self.client.post(reverse("frequency_api"), {"date": "2025-01-01"})
        self.assertEqual(response.status_code, 400)

    def test_frequency_post_creates(self):
        response = self.client.post(
            reverse("frequency_api"),
            {"student_id": self.student.id, "date": "2025-01-01"},
            format="json",
        )
        self.assertEqual(response.status_code, 201)

    def test_frequency_delete_missing(self):
        response = self.client.delete(
            reverse("frequency_api"),
            {"student_id": self.student.id, "date": "2025-01-02"},
            format="json",
        )
        self.assertEqual(response.status_code, 404)

    def test_frequency_delete_success(self):
        self.client.post(
            reverse("frequency_api"),
            {"student_id": self.student.id, "date": "2025-01-01"},
            format="json",
        )
        response = self.client.delete(
            reverse("frequency_api"),
            {"student_id": self.student.id, "date": "2025-01-01"},
            format="json",
        )
        self.assertEqual(response.status_code, 204)

    def test_frequency_delete_requires_student(self):
        response = self.client.delete(
            reverse("frequency_api"),
            {"date": "2025-01-01"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_frequency_get_default_date(self):
        response = self.client.get(reverse("frequency_api"))
        self.assertEqual(response.status_code, 200)

    def test_student_activate_requires_payments(self):
        response = self.client.post(
            reverse("student_activate", args=[self.student.id]),
            {"student": {}, "payment": {}},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_student_activate_invalid_total_amount(self):
        payload = {
            "student": {"plan": self.plan.id},
            "payment": {
                "amount": "0.00",
                "discount_percent": "0.00",
                "discount_value": "0.00",
                "payments": [
                    {
                        "payment_method": "pix",
                        "value": "0.00",
                        "quantity_installments": 1,
                    }
                ],
            },
        }
        response = self.client.post(
            reverse("student_activate", args=[self.student.id]),
            payload,
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_student_activate_invalid_payment_method(self):
        payload = {
            "student": {"plan": self.plan.id},
            "payment": {
                "amount": "100.00",
                "discount_percent": "0.00",
                "discount_value": "0.00",
                "payments": [{"payment_method": "", "value": "100.00"}],
            },
        }
        response = self.client.post(
            reverse("student_activate", args=[self.student.id]),
            payload,
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_student_activate_mismatched_total(self):
        payload = {
            "student": {"plan": self.plan.id},
            "payment": {
                "amount": "100.00",
                "discount_percent": "0.00",
                "discount_value": "0.00",
                "payments": [
                    {
                        "payment_method": "pix",
                        "value": "90.00",
                        "quantity_installments": 1,
                    }
                ],
            },
        }
        response = self.client.post(
            reverse("student_activate", args=[self.student.id]),
            payload,
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_student_activate_invalid_birth_date(self):
        payload = {
            "student": {"plan": self.plan.id, "date_of_birth": "invalid"},
            "payment": {
                "amount": "100.00",
                "discount_percent": "0.00",
                "discount_value": "0.00",
                "payments": [{"payment_method": "pix", "value": "100.00"}],
            },
        }
        response = self.client.post(
            reverse("student_activate", args=[self.student.id]),
            payload,
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_student_activate_invalid_plan_type(self):
        payload = {
            "student": {"plan": "not-a-number"},
            "payment": {
                "amount": "100.00",
                "discount_percent": "0.00",
                "discount_value": "0.00",
                "payments": [{"payment_method": "pix", "value": "100.00"}],
            },
        }
        response = self.client.post(
            reverse("student_activate", args=[self.student.id]),
            payload,
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_student_activate_invalid_discount(self):
        payload = {
            "student": {"plan": self.plan.id},
            "payment": {
                "amount": "100.00",
                "discount_percent": "not-a-number",
                "discount_value": "0.00",
                "payments": [{"payment_method": "pix", "value": "100.00"}],
            },
        }
        response = self.client.post(
            reverse("student_activate", args=[self.student.id]),
            payload,
            format="json",
        )
        self.assertEqual(response.status_code, 200)

    def test_student_activate_clears_birth_date(self):
        payload = {
            "student": {"plan": self.plan.id, "date_of_birth": ""},
            "payment": {
                "amount": "100.00",
                "discount_percent": "0.00",
                "discount_value": "0.00",
                "payments": [{"payment_method": "pix", "value": "100.00"}],
            },
        }
        response = self.client.post(
            reverse("student_activate", args=[self.student.id]),
            payload,
            format="json",
        )
        self.assertEqual(response.status_code, 200)

    def test_student_activate_invalid_plan(self):
        payload = {
            "student": {"plan": 99999},
            "payment": {
                "amount": "100.00",
                "discount_percent": "0.00",
                "discount_value": "0.00",
                "payments": [
                    {
                        "payment_method": "pix",
                        "value": "100.00",
                        "quantity_installments": 1,
                    }
                ],
            },
        }
        response = self.client.post(
            reverse("student_activate", args=[self.student.id]),
            payload,
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_student_activate_success(self):
        payload = {
            "student": {
                "name": "Student A",
                "plan": self.plan.id,
                "date_of_birth": "2000-01-01",
            },
            "payment": {
                "amount": "100.00",
                "discount_percent": "0.00",
                "discount_value": "0.00",
                "payments": [
                    {
                        "payment_method": "pix",
                        "value": "100.00",
                        "quantity_installments": 1,
                    }
                ],
            },
        }
        response = self.client.post(
            reverse("student_activate", args=[self.student.id]),
            payload,
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.student.refresh_from_db()
        self.assertEqual(self.student.status, self.status_active)
        self.assertEqual(MonthlyFee.objects.filter(student=self.student).count(), 1)


class MonthlyFeeApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        User = get_user_model()
        self.user = User.objects.create_user(
            username="tester",
            password="strong-password-123",
        )
        self.client.force_authenticate(self.user)

        self.status = StatusStudent.objects.create(status="Ativo")
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
        self.monthly_fee = MonthlyFee.objects.create(
            student=self.student,
            student_name=self.student.name,
            amount=Decimal("100.00"),
            due_date=date.today(),
            reference_month="01/2025",
            paid=False,
            plan=self.plan,
        )

    def test_monthly_fee_update_marks_paid(self):
        response = self.client.put(
            reverse("monthlyfee_api", args=[self.monthly_fee.id]),
            {
                "student_name": self.student.name,
                "discount_percent": "0.00",
                "discount_value": "0.00",
                "amount": "100.00",
                "payments": [
                    {
                        "payment_method": "pix",
                        "value": "100.00",
                        "quantity_installments": 1,
                    }
                ],
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.monthly_fee.refresh_from_db()
        self.assertTrue(self.monthly_fee.paid)

    def test_monthly_fee_retrieve_not_found(self):
        response = self.client.get(reverse("monthlyfee_api", args=[9999]))
        self.assertEqual(response.status_code, 404)

    def test_monthly_fee_requires_auth(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(
            reverse("monthlyfee_api", args=[self.monthly_fee.id])
        )
        self.assertEqual(response.status_code, 403)


class StudentCrudApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        User = get_user_model()
        self.user = User.objects.create_user(
            username="tester",
            password="strong-password-123",
        )
        self.client.force_authenticate(self.user)
        self.status_active = StatusStudent.objects.create(status="Ativo")
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
            due_date=1,
            plan=self.plan,
        )

    def test_student_retrieve(self):
        response = self.client.get(reverse("student_api", args=[self.student.id]))
        self.assertEqual(response.status_code, 200)

    def test_student_update_invalid_status(self):
        response = self.client.put(
            reverse("student_api", args=[self.student.id]),
            {"status": 9999},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_student_delete(self):
        response = self.client.delete(reverse("student_api", args=[self.student.id]))
        self.assertEqual(response.status_code, 204)


class StatusStudentApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        User = get_user_model()
        self.user = User.objects.create_user(
            username="tester",
            password="strong-password-123",
        )
        self.client.force_authenticate(self.user)

    def test_status_list(self):
        response = self.client.get(reverse("status_api"))
        self.assertEqual(response.status_code, 200)

    def test_status_create_missing(self):
        response = self.client.post(reverse("status_api"), {})
        self.assertEqual(response.status_code, 400)


class PaymentApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        User = get_user_model()
        self.user = User.objects.create_user(
            username="tester",
            password="strong-password-123",
        )
        self.client.force_authenticate(self.user)

    def test_payment_list(self):
        response = self.client.get(reverse("payment_api"))
        self.assertEqual(response.status_code, 200)

    def test_payment_create_missing_monthlyfee(self):
        self.client.raise_request_exception = False
        response = self.client.post(
            reverse("payment_api"),
            {"payment_method": "pix", "value": "10.00", "quantity_installments": 1},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
