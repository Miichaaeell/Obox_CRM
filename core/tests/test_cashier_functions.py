from datetime import date, datetime
from decimal import Decimal

from django.test import TestCase

from core.functions import (
    close_cashier,
    create_file_xlsx_cashier,
    create_new_register_cashier,
    get_context_cashier_data,
)
from unittest.mock import patch
from enterprise.models import Bill, Cashier, PaymentMethod, StatusBill, Plan
from students.models import MonthlyFee, Payment, StatusStudent, Student


class CashierFunctionTests(TestCase):
    def setUp(self):
        self.status_student = StatusStudent.objects.create(status="Ativo")
        self.plan = Plan.objects.create(
            name_plan="Plan A",
            description="Test",
            price=Decimal("100.00"),
            duration_months=12,
        )
        self.student = Student.objects.create(
            name="Student A",
            cpf_cnpj="12345678901",
            status=self.status_student,
            observation="Test",
            due_date=1,
            plan=self.plan,
        )
        self.payment_method = PaymentMethod.objects.create(method="Pix")
        self.automatic_method = PaymentMethod.objects.create(method="deb. automatico")
        self.status_bill = StatusBill.objects.create(status="PENDENTE")
        self.status_automatic = StatusBill.objects.create(status="automatico")

    def test_create_new_register_cashier(self):
        response = create_new_register_cashier()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Cashier.objects.filter(status="open").count(), 1)

        response_duplicate = create_new_register_cashier()
        self.assertEqual(response_duplicate.status_code, 400)

    def test_create_new_register_cashier_error(self):
        with patch(
            "core.functions.Cashier.objects.create", side_effect=Exception("boom")
        ):
            response = create_new_register_cashier()
        self.assertEqual(response.status_code, 400)

    def test_get_context_cashier_data_closed(self):
        cashier = Cashier.objects.create(
            status="closed",
            income_pix=Decimal("10.00"),
            total_incomes=Decimal("10.00"),
            total_expenses=Decimal("5.00"),
            closing_balance=Decimal("5.00"),
        )
        context = get_context_cashier_data()
        self.assertEqual(context["status"], cashier.get_status_display())

    def test_get_context_cashier_data_open(self):
        Cashier.objects.create(status="open")
        context = get_context_cashier_data()
        self.assertIn("payments", context)

    def test_close_cashier_updates(self):
        cashier = Cashier.objects.create(status="open")
        monthly = MonthlyFee.objects.create(
            student=self.student,
            student_name=self.student.name,
            amount=Decimal("100.00"),
            due_date=date.today(),
            reference_month="01/2025",
            paid=True,
            plan=self.plan,
        )
        Payment.objects.create(
            montlhyfee=monthly,
            payment_method="pix",
            value=Decimal("100.00"),
            quantity_installments=1,
        )
        Payment.objects.create(
            montlhyfee=monthly,
            payment_method="credito",
            value=Decimal("50.00"),
            quantity_installments=1,
        )
        automatic_method = PaymentMethod.objects.create(method="deb. automatico")
        automatic_status = StatusBill.objects.create(status="automatico")
        Bill.objects.create(
            description="Conta",
            value=Decimal("50.00"),
            due_date=date.today(),
            status=self.status_bill,
            payment_method=self.payment_method,
        )
        Bill.objects.create(
            description="Conta Auto",
            value=Decimal("30.00"),
            due_date=date.today(),
            status=automatic_status,
            payment_method=automatic_method,
        )
        context = get_context_cashier_data()
        response = close_cashier(context, withdrawalValue=0, closing_balance=50)
        cashier.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(cashier.status, "closed")

    def test_close_cashier_error(self):
        with patch(
            "core.functions.Cashier.objects.order_by", side_effect=Exception("boom")
        ):
            response = close_cashier(
                {
                    "total_incomes": 0,
                    "total_expenses": 0,
                    "income_pix": 0,
                    "income_credit": 0,
                    "income_debit": 0,
                    "income_cash": 0,
                    "expense_pix": 0,
                    "expense_boleto": 0,
                    "expense_automatic": 0,
                    "expense_others": 0,
                    "payments": Payment.objects.none(),
                    "bills": Bill.objects.none(),
                },
                0,
                0,
            )
        self.assertEqual(response.status_code, 400)

    def test_create_file_xlsx_cashier(self):
        cashier = Cashier.objects.create(status="closed", date_closing=datetime.now())
        monthly = MonthlyFee.objects.create(
            student=self.student,
            student_name=self.student.name,
            amount=Decimal("100.00"),
            due_date=date.today(),
            reference_month="01/2025",
            paid=True,
            plan=self.plan,
        )
        Payment.objects.create(
            montlhyfee=monthly,
            payment_method="pix",
            value=Decimal("100.00"),
            quantity_installments=1,
            cashier=cashier,
        )
        Bill.objects.create(
            description="Conta Sem Pagamento",
            value=Decimal("10.00"),
            due_date=date.today(),
            status=self.status_bill,
            payment_method=None,
            cashier=cashier,
        )
        buffer, name = create_file_xlsx_cashier(cashier)
        self.assertTrue(name.endswith(".xlsx"))
        self.assertGreater(len(buffer.getvalue()), 0)
