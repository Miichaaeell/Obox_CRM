from datetime import date
from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase

from enterprise.models import Bill, Enterprise, PaymentMethod, StatusBill
from enterprise.tasks import create_recurring_bill, send_NFS
from students.models import StatusStudent, Student
from enterprise.models import Plan


class RecurringBillTaskTests(TestCase):
    def setUp(self):
        self.status_pending = StatusBill.objects.create(status="PENDENTE")
        self.status_auto = StatusBill.objects.create(status="automatico")
        self.method_auto = PaymentMethod.objects.create(method="deb. automatico")
        self.method_cash = PaymentMethod.objects.create(method="Dinheiro")

    def test_create_recurring_bill_auto_and_non_auto(self):
        Bill.objects.create(
            description="Conta Auto",
            value=Decimal("10.00"),
            due_date=date.today().replace(day=1),
            status=self.status_pending,
            payment_method=self.method_auto,
            appellant=True,
        )
        Bill.objects.create(
            description="Conta Manual",
            value=Decimal("20.00"),
            due_date=date.today().replace(day=1),
            status=self.status_pending,
            payment_method=self.method_cash,
            appellant=True,
        )
        with patch(
            "enterprise.tasks.StatusBill.objects.get_or_create",
            return_value=(self.status_pending, False),
        ):
            result = create_recurring_bill()
        self.assertIn("Create", result)


class SendNfsTaskTests(TestCase):
    def setUp(self):
        self.enterprise = Enterprise.objects.create(
            name="Empresa",
            cnpj="01.234.567/0001-90",
            description_service="Serviço",
            service_code="1234",
            iss_retained=False,
            iss_aliquot=Decimal("0.05"),
        )
        self.status_active = StatusStudent.objects.create(status="Ativo")
        self.plan = Plan.objects.create(
            name_plan="Plan A",
            description="Test",
            price="100.00",
            duration_months=12,
        )
        self.student = Student.objects.create(
            name="Aluno",
            cpf_cnpj="12345678901",
            status=self.status_active,
            observation="Test",
            due_date=1,
            plan=self.plan,
        )

    @patch("enterprise.tasks.config")
    @patch("enterprise.tasks.WebmaniaClient")
    def test_send_nfs_success(self, mock_client_cls, mock_config):
        mock_config.side_effect = lambda key, default=None: (
            "token" if "TOKEN" in key else 2
        )
        mock_client = mock_client_cls.return_value
        mock_client.send_nfs.return_value = {
            "uuid": "uuid",
            "pdf_rps": "pdf",
            "xml": "xml",
        }
        payload = {
            "student": [{"cpf": "123", "name": "Aluno", "valor": "100.00"}],
            "description": "Servico",
            "reference_month": "01/2025",
        }
        result = send_NFS(payload)
        self.assertIn("notas emitidas", result)

    @patch("enterprise.tasks.config")
    @patch("enterprise.tasks.WebmaniaClient")
    def test_send_nfs_iss_retained_payload(self, mock_client_cls, mock_config):
        self.enterprise.iss_retained = True
        self.enterprise.save()
        mock_config.side_effect = lambda key, default=None: (
            "token" if "TOKEN" in key else 2
        )
        mock_client = mock_client_cls.return_value
        mock_client.send_nfs.return_value = {"uuid": "uuid"}
        payload = {
            "student": [{"cpf": "123", "name": "Aluno", "valor": "100.00"}],
            "description": "Servico",
            "reference_month": "01/2025",
        }
        send_NFS(payload)
        sent_payload = mock_client.send_nfs.call_args[1]["data"]
        self.assertEqual(sent_payload["servico"]["responsavel_retencao_iss"], 1)

    @patch("enterprise.tasks.NFSe")
    @patch("enterprise.tasks.config")
    @patch("enterprise.tasks.WebmaniaClient")
    def test_send_nfs_nfse_create_error(self, mock_client_cls, mock_config, mock_nfse):
        mock_config.side_effect = lambda key, default=None: (
            "token" if "TOKEN" in key else 2
        )
        mock_client = mock_client_cls.return_value
        mock_client.send_nfs.return_value = {"uuid": "uuid"}
        mock_nfse.side_effect = RuntimeError("nfse error")
        payload = {
            "student": [{"cpf": "123", "name": "Aluno", "valor": "100.00"}],
            "description": "Servico",
            "reference_month": "01/2025",
        }
        result = send_NFS(payload)
        self.assertIn("notas emitidas", result)

    @patch("enterprise.tasks.config")
    @patch("enterprise.tasks.WebmaniaClient")
    def test_send_nfs_error_response(self, mock_client_cls, mock_config):
        mock_config.side_effect = lambda key, default=None: (
            "token" if "TOKEN" in key else 2
        )
        mock_client = mock_client_cls.return_value
        mock_client.send_nfs.return_value = {"error": "fail"}
        payload = {
            "student": [{"cpf": "123", "name": "Aluno", "valor": "100.00"}],
            "description": "Servico",
            "reference_month": "01/2025",
        }
        result = send_NFS(payload)
        self.assertIn("falharam", result)

    @patch("enterprise.tasks.config")
    @patch("enterprise.tasks.WebmaniaClient")
    def test_send_nfs_exception_during_send(self, mock_client_cls, mock_config):
        mock_config.side_effect = lambda key, default=None: (
            "token" if "TOKEN" in key else 2
        )
        mock_client = mock_client_cls.return_value
        mock_client.send_nfs.side_effect = RuntimeError("boom")
        payload = {
            "student": [{"cpf": "123", "name": "Aluno", "valor": "100.00"}],
            "description": "Servico",
            "reference_month": "01/2025",
        }
        result = send_NFS(payload)
        self.assertIn("falharam", result)
