from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient

from enterprise.models import PaymentMethod, StatusBill


@override_settings(
    STORAGES={
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        }
    }
)
class EnterpriseViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        User = get_user_model()
        self.user = User.objects.create_user(
            username="tester",
            password="strong-password-123",
        )
        self.status_bill = StatusBill.objects.create(status="PENDENTE")

    def test_home_requires_login(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_home_renders_for_authenticated_user(self):
        self.client.login(username="tester", password="strong-password-123")
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

    def test_nfse_api_invalid_payload(self):
        self.client.force_authenticate(self.user)
        response = self.client.post(reverse("nfe_api"), {"description": "Test"})
        self.assertEqual(response.status_code, 400)

    @patch("enterprise.views.send_NFS")
    def test_nfse_api_valid_payload_schedules_task(self, mock_send):
        self.client.force_authenticate(self.user)
        response = self.client.post(
            reverse("nfe_api"),
            {
                "student": [{"id": 1, "name": "A"}],
                "description": "Servico",
                "reference_month": "01/2025",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 202)
        mock_send.delay.assert_called_once()

    def test_create_plan_missing_fields_returns_400(self):
        response = self.client.post(reverse("plan_api"), {"name_plan": "Plan A"})
        self.assertEqual(response.status_code, 400)

    def test_create_plan_success(self):
        response = self.client.post(
            reverse("plan_api"),
            {
                "name_plan": "Plan A",
                "description": "Test",
                "price": "100.00",
                "duration_months": 12,
            },
        )
        self.assertEqual(response.status_code, 201)

    def test_list_plans(self):
        response = self.client.get(reverse("plan_api"))
        self.assertEqual(response.status_code, 200)

    def test_create_service_missing_fields_returns_400(self):
        response = self.client.post(reverse("service_api"), {"service": "Consulting"})
        self.assertEqual(response.status_code, 400)

    def test_create_service_success(self):
        response = self.client.post(
            reverse("service_api"),
            {"service": "Consulting", "price": "50.00"},
        )
        self.assertEqual(response.status_code, 201)

    def test_list_services(self):
        response = self.client.get(reverse("service_api"))
        self.assertEqual(response.status_code, 200)

    def test_create_payment_method_missing_fields_returns_400(self):
        response = self.client.post(reverse("payment_method"), {})
        self.assertEqual(response.status_code, 400)

    def test_create_payment_method_success(self):
        response = self.client.post(
            reverse("payment_method"),
            {"method": "Pix", "applies_to": "students"},
        )
        self.assertEqual(response.status_code, 201)

    def test_list_payment_methods(self):
        response = self.client.get(reverse("payment_method"))
        self.assertEqual(response.status_code, 200)

    def test_create_enterprise_missing_fields_returns_400(self):
        response = self.client.post(reverse("enterprise_api"), {"name": "Empresa"})
        self.assertEqual(response.status_code, 400)

    def test_create_enterprise_success(self):
        response = self.client.post(
            reverse("enterprise_api"),
            {
                "name": "Empresa A",
                "cnpj": "01.234.567/0001-90",
                "description_service": "Serviço",
            },
        )
        self.assertEqual(response.status_code, 201)

    def test_list_enterprises(self):
        response = self.client.get(reverse("enterprise_api"))
        self.assertEqual(response.status_code, 200)

    def test_create_bill_missing_fields_returns_400(self):
        response = self.client.post(reverse("create_bill"), {"description": "Conta"})
        self.assertEqual(response.status_code, 400)

    def test_create_bill_success(self):
        payment_method = PaymentMethod.objects.create(method="Pix")
        response = self.client.post(
            reverse("create_bill"),
            {
                "description": "Conta",
                "value": "50.00",
                "due_date": "2025-01-01",
                "status": self.status_bill.id,
                "payment_method": payment_method.id,
            },
        )
        self.assertEqual(response.status_code, 201)

    def test_list_bills(self):
        response = self.client.get(reverse("create_bill"))
        self.assertEqual(response.status_code, 200)

    def test_retrieve_missing_plan_returns_404(self):
        response = self.client.get(reverse("plan_api", args=[9999]))
        self.assertEqual(response.status_code, 404)

    def test_retrieve_missing_service_returns_404(self):
        response = self.client.get(reverse("service_api", args=[9999]))
        self.assertEqual(response.status_code, 404)

    def test_retrieve_missing_payment_method_returns_404(self):
        response = self.client.get(reverse("payment_method", args=[9999]))
        self.assertEqual(response.status_code, 404)

    def test_retrieve_missing_bill_returns_404(self):
        response = self.client.get(reverse("detail_bill", args=[9999]))
        self.assertEqual(response.status_code, 404)

    def test_enterprise_update_invalid_returns_400(self):
        response = self.client.put(
            reverse("enterprise_api", args=[1]),
            {"cnpj": "invalid"},
            format="json",
        )
        self.assertIn(response.status_code, (400, 404))
