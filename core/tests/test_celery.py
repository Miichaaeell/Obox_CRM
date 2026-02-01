from django.test import SimpleTestCase

from core.celery import app, debug_task


class DummyTask:
    def __repr__(self):
        return "<DummyTask>"


class CeleryTests(SimpleTestCase):
    def test_app_configured(self):
        self.assertEqual(app.main, "core")

    def test_debug_task_runs(self):
        self.assertTrue(hasattr(debug_task, "__wrapped__"))
        debug_task.__wrapped__()
