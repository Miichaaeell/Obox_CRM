from io import BytesIO
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from enterprise.models import Cashier


@override_settings(
    STORAGES={
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        }
    }
)
class EnterprisePageViewTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="tester",
            password="strong-password-123",
        )
        self.client.login(username="tester", password="strong-password-123")

    def test_home_page(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_page(self):
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_settings_page(self):
        response = self.client.get(reverse("settings"))
        self.assertEqual(response.status_code, 200)

    def test_bill_list_page(self):
        response = self.client.get(reverse("list_bill"))
        self.assertEqual(response.status_code, 200)

    def test_bill_list_search_filters(self):
        from enterprise.models import Bill, PaymentMethod, StatusBill
        from datetime import date
        from decimal import Decimal

        status = StatusBill.objects.create(status="PENDENTE")
        method = PaymentMethod.objects.create(method="Pix")
        Bill.objects.create(
            description="Conta",
            value=Decimal("10.00"),
            due_date=date(2025, 1, 15),
            status=status,
            payment_method=method,
        )
        response = self.client.get(
            reverse("list_bill"),
            {"search": "15/01/2025"},
        )
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse("list_bill"), {"search": "2025-01-15"})
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse("list_bill"), {"search": "01/2025"})
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse("list_bill"), {"search": "PEND"})
        self.assertEqual(response.status_code, 200)

    def test_cashier_page(self):
        response = self.client.get(reverse("cashier"))
        self.assertEqual(response.status_code, 200)

    def test_flow_cashier_page(self):
        response = self.client.get(reverse("flow_cashier"))
        self.assertEqual(response.status_code, 200)

    def test_nfes_page(self):
        response = self.client.get(reverse("nfes"))
        self.assertEqual(response.status_code, 200)

    def test_download_cashier_missing_returns_404(self):
        response = self.client.get(reverse("download_cashier"))
        self.assertEqual(response.status_code, 404)

    def test_download_cashier_valid_returns_file(self):
        cashier = Cashier.objects.create(status="closed")
        with patch("enterprise.views.create_file_xlsx_cashier") as mock_create:
            mock_create.return_value = (BytesIO(b"data"), "file.xlsx")
            response = self.client.get(reverse("download_cashier"), {"pk": cashier.id})
            self.assertEqual(response.status_code, 200)

    def test_cashier_post_create_and_update(self):
        response = self.client.post(
            reverse("cashier"),
            data='{"action":"create"}',
            content_type="application/json",
        )
        self.assertIn(response.status_code, (200, 201, 400))
        response = self.client.post(
            reverse("cashier"),
            data='{"action":"update","withdrawalValue":0,"closing_balance":0}',
            content_type="application/json",
        )
        self.assertIn(response.status_code, (200, 400))
