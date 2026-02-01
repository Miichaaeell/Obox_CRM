from django.db import models
from django.test import SimpleTestCase
from rest_framework import status

from core.exceptions import custom_exception_handler


class DummyModel(models.Model):
    class Meta:
        app_label = "core"


class ExceptionHandlerTests(SimpleTestCase):
    def test_protected_error_returns_409(self):
        exc = models.ProtectedError("Protected", protected_objects=[])
        response = custom_exception_handler(exc, context={})
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertIn("detail", response.data)
