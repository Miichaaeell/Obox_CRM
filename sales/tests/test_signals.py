from decimal import Decimal

from django.test import TestCase

from enterprise.models import PaymentMethod
from sales.models import Intflow, Product, ProductStock, Sale


class SalesSignalsTests(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Product A",
            description="Test",
            price=Decimal("10.00"),
        )
        self.payment_method = PaymentMethod.objects.create(method="Pix")

    def test_intflow_creates_stock(self):
        Intflow.objects.create(product=self.product, quantity=5, description="Init")
        stock = ProductStock.objects.get(product=self.product)
        self.assertEqual(stock.quantity, 5)

    def test_intflow_updates_stock(self):
        Intflow.objects.create(product=self.product, quantity=5)
        Intflow.objects.create(product=self.product, quantity=3)
        stock = ProductStock.objects.get(product=self.product)
        self.assertEqual(stock.quantity, 8)

    def test_sale_reduces_stock(self):
        ProductStock.objects.create(product=self.product, quantity=10)
        Sale.objects.create(
            product=self.product,
            value_unitary=Decimal("10.00"),
            quantity=4,
            discount_value=Decimal("0.00"),
            discount_percent=Decimal("0.00"),
            total_price=Decimal("40.00"),
            payment_method=self.payment_method,
        )
        stock = ProductStock.objects.get(product=self.product)
        self.assertEqual(stock.quantity, 6)

    def test_sale_insufficient_stock_raises(self):
        ProductStock.objects.create(product=self.product, quantity=2)
        with self.assertRaises(ValueError):
            Sale.objects.create(
                product=self.product,
                value_unitary=Decimal("10.00"),
                quantity=3,
                discount_value=Decimal("0.00"),
                discount_percent=Decimal("0.00"),
                total_price=Decimal("30.00"),
                payment_method=self.payment_method,
            )
