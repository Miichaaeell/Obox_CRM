from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse


@override_settings(
    STORAGES={
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        }
    }
)
class SalesViewTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="tester",
            password="strong-password-123",
        )

    def test_product_list_requires_login(self):
        response = self.client.get(reverse("list_product"))
        self.assertEqual(response.status_code, 302)

    def test_product_list_authenticated(self):
        self.client.login(username="tester", password="strong-password-123")
        response = self.client.get(reverse("list_product"))
        self.assertEqual(response.status_code, 200)

    def test_stock_dashboard_authenticated(self):
        self.client.login(username="tester", password="strong-password-123")
        response = self.client.get(reverse("list_stock"))
        self.assertEqual(response.status_code, 200)

    def test_product_create_page_authenticated(self):
        self.client.login(username="tester", password="strong-password-123")
        response = self.client.get(reverse("create_product"))
        self.assertEqual(response.status_code, 200)

    def test_product_update_page_authenticated(self):
        self.client.login(username="tester", password="strong-password-123")
        response = self.client.get(reverse("update_product", args=[1]))
        self.assertIn(response.status_code, (200, 404))

    def test_intflow_create_page_authenticated(self):
        self.client.login(username="tester", password="strong-password-123")
        response = self.client.get(reverse("create_intflow"))
        self.assertEqual(response.status_code, 200)
