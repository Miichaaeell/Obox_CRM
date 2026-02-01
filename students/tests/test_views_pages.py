from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from enterprise.models import Installments, PaymentMethod, Plan, Service
from students.models import StatusStudent, Student


@override_settings(
    STORAGES={
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        }
    }
)
class StudentPageViewTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="tester",
            password="strong-password-123",
        )
        self.client.login(username="tester", password="strong-password-123")
        self.status_active = StatusStudent.objects.create(status="ATIVO")
        self.plan = Plan.objects.create(
            name_plan="Plan A",
            description="Test",
            price=Decimal("100.00"),
            duration_months=12,
        )
        PaymentMethod.objects.create(method="Pix", applies_to="students")
        Installments.objects.create(quantity_installments=1)
        Service.objects.create(service="Matrícula", price=Decimal("10.00"))
        self.student = Student.objects.create(
            name="Student A",
            cpf_cnpj="12345678901",
            status=self.status_active,
            observation="Test",
            due_date=1,
            plan=self.plan,
        )

    def test_list_students_page(self):
        response = self.client.get(reverse("list_student"))
        self.assertEqual(response.status_code, 200)

    def test_list_students_filters(self):
        response = self.client.get(reverse("list_student"), {"filter": "ativo"})
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse("list_student"), {"filter": "inativo"})
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse("list_student"), {"filter": "avencer"})
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse("list_student"), {"filter": "atrasado"})
        self.assertEqual(response.status_code, 200)

    def test_create_student_page(self):
        response = self.client.get(reverse("create_student"))
        self.assertEqual(response.status_code, 200)

    def test_create_student_post(self):
        StatusStudent.objects.get_or_create(status="ATIVO")
        payload = {
            "name": "Novo Aluno",
            "cpf_cnpj": "12345678901",
            "date_of_birth": "2000-01-01",
            "phone_number": "11999999999",
            "plan": self.plan.id,
            "value_receiver": "R$ 100,00",
            "percent_discount": "0",
            "discount_value": "0",
            "payments": '[{"payment_method":"pix","value":"100.00","quantity_installments":1}]',
        }
        response = self.client.post(reverse("create_student"), data=payload)
        self.assertIn(response.status_code, (200, 302))

    def test_create_student_form_valid(self):
        from django.test import RequestFactory
        from students.forms import StudentForm
        from students.views import StudentCreateView

        StatusStudent.objects.get_or_create(status="ATIVO")
        payload = {
            "name": "Aluno Form",
            "cpf_cnpj": "12345678902",
            "date_of_birth": "2000-01-01",
            "phone_number": "11999999999",
            "plan": self.plan.id,
            "value_receiver": "R$ 100,00",
            "percent_discount": "0",
            "discount_value": "0",
            "payments": '[{"payment_method":"pix","value":"100.00","quantity_installments":1}]',
        }
        form = StudentForm(data=payload)
        self.assertTrue(form.is_valid(), form.errors)
        request = RequestFactory().post(reverse("create_student"), data=payload)
        request.user = self.user
        view = StudentCreateView()
        view.request = request
        response = view.form_valid(form)
        self.assertEqual(response.status_code, 302)

    def test_detail_student_page(self):
        response = self.client.get(reverse("detail_student", args=[self.student.id]))
        self.assertEqual(response.status_code, 200)

    def test_status_list_page(self):
        response = self.client.get(reverse("list_status"))
        self.assertEqual(response.status_code, 200)

    def test_status_create_page(self):
        response = self.client.get(reverse("create_status"))
        self.assertEqual(response.status_code, 200)

    def test_status_update_page(self):
        response = self.client.get(
            reverse("update_status", args=[self.status_active.id])
        )
        self.assertEqual(response.status_code, 200)

    def test_frequency_page(self):
        response = self.client.get(reverse("frequence"))
        self.assertEqual(response.status_code, 200)

    def test_uploadfile_without_file_sets_message(self):
        with patch("students.views.messages") as mock_messages:
            response = self.client.post(reverse("uploadfile"), data={})
            self.assertEqual(response.status_code, 302)
            mock_messages.error.assert_called()
