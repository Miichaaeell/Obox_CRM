from datetime import date
from decimal import Decimal

from django.test import TestCase

from enterprise.models import (
    Bill,
    Cashier,
    Enterprise,
    Installments,
    NFSe,
    PaymentMethod,
    Plan,
    Service,
    StatusBill,
    TypeBill,
)
from students.models import StatusStudent, Student


class EnterpriseModelTests(TestCase):
    def setUp(self):
        self.status = StatusStudent.objects.create(status="Ativo")
        self.status_pending = StatusBill.objects.create(status="PENDENTE")
        self.status_auto = StatusBill.objects.create(status="automatico")
        self.method_auto = PaymentMethod.objects.create(method="deb. automatico")
        self.method_cash = PaymentMethod.objects.create(method="Dinheiro")
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

    def test_enterprise_str(self):
        enterprise = Enterprise.objects.create(
            name="Empresa X",
            cnpj="01.234.567/0001-90",
            description_service="Service",
        )
        self.assertEqual(str(enterprise), "Empresa X")

    def test_service_str(self):
        service = Service.objects.create(service="Consulting", price=Decimal("50.00"))
        self.assertEqual(str(service), "Consulting - 50.00")

    def test_status_bill_str(self):
        status = StatusBill.objects.create(status="Pendente")
        self.assertEqual(str(status), "Pendente")

    def test_type_bill_str(self):
        bill_type = TypeBill.objects.create(type_bill="Energia")
        self.assertEqual(str(bill_type), "Energia")

    def test_payment_method_str(self):
        method = PaymentMethod.objects.create(method="Pix", applies_to="students")
        self.assertEqual(str(method), "Pix")

    def test_cashier_str(self):
        cashier = Cashier.objects.create(status="open")
        self.assertIn("/", str(cashier))

    def test_plan_str(self):
        self.assertEqual(str(self.plan), "Plan A")

    def test_nfse_str(self):
        nfse = NFSe.objects.create(
            student=self.student,
            uuid_nfse="abc-123",
            reference_month="01/2025",
        )
        self.assertIn("NFSe abc-123", str(nfse))

    def test_installments_str(self):
        installments = Installments.objects.create(quantity_installments=3)
        self.assertEqual(str(installments), "3x")

    def test_bill_str(self):
        bill = Bill.objects.create(
            description="Conta Luz",
            value=Decimal("100.00"),
            due_date=date.today(),
            status=self.status_pending,
            payment_method=self.method_cash,
        )
        self.assertEqual(str(bill), "Conta Luz")
