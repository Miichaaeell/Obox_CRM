from django.test import SimpleTestCase

from core.templatetags.format_extras import (
    calculate_lucrativity,
    month_name,
    subtract,
)


class FormatExtrasTests(SimpleTestCase):
    def test_month_name_from_dash(self):
        self.assertEqual(month_name("2025-09"), "Setembro/2025")

    def test_month_name_from_slash(self):
        self.assertEqual(month_name("9/2025"), "Setembro/2025")

    def test_month_name_invalid_returns_input(self):
        value = "not-a-date"
        self.assertEqual(month_name(value), value)

    def test_calculate_lucrativity(self):
        self.assertEqual(calculate_lucrativity(200, 50), "75.00")

    def test_calculate_lucrativity_zero_income(self):
        self.assertEqual(calculate_lucrativity(0, 50), "0.00")

    def test_calculate_lucrativity_invalid(self):
        self.assertEqual(calculate_lucrativity("x", "y"), "0.00")

    def test_subtract_invalid_returns_zero(self):
        self.assertEqual(subtract("x", 1), 0)
