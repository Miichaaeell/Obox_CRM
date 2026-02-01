from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test import override_settings
from django.urls import reverse


@override_settings(
    STORAGES={
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        }
    }
)
class LoginLogoutViewTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="tester",
            password="strong-password-123",
        )

    def test_login_get_renders(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)

    def test_login_invalid_shows_error(self):
        response = self.client.post(
            reverse("login"),
            {"username": "tester", "password": "wrong"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context.get("error"), "Usuário ou senha inválidos.")

    def test_login_valid_redirects_home(self):
        response = self.client.post(
            reverse("login"),
            {"username": "tester", "password": "strong-password-123"},
        )
        self.assertRedirects(response, reverse("home"), fetch_redirect_response=False)

    def test_logout_redirects_login(self):
        self.client.login(username="tester", password="strong-password-123")
        response = self.client.get(reverse("logout"))
        self.assertRedirects(response, reverse("login"))
