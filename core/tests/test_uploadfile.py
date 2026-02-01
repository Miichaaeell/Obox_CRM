from datetime import datetime
from unittest.mock import patch

import pandas as pd
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from core.uploadfile import format_cpf, upload_file
from enterprise.models import Plan
from students.models import MonthlyFee, StatusStudent, Student


class UploadFileTests(TestCase):
    def setUp(self):
        self.status = StatusStudent.objects.create(status="Ativo")
        self.plan = Plan.objects.create(
            name_plan="Plan A",
            description="Test",
            price="100.00",
            duration_months=12,
        )

    def test_format_cpf(self):
        self.assertEqual(format_cpf("123.456.789-01"), "123.456.789-01")
        self.assertEqual(format_cpf("12345678901"), "123.456.789-01")
        self.assertEqual(format_cpf("1"), "000.000.000-01")

    def test_upload_file_invalid_extension(self):
        file = SimpleUploadedFile("data.txt", b"content")
        response = upload_file(file)
        self.assertEqual(response["status_code"], "400")

    def test_upload_file_missing_columns_returns_422(self):
        df = pd.DataFrame([{"foo": "bar"}])
        file = SimpleUploadedFile("data.csv", b"content")
        with patch("core.uploadfile.pd.read_csv", return_value=df):
            response = upload_file(file)
        self.assertEqual(response["status_code"], "422")

    def test_upload_file_missing_plan_returns_422(self):
        df = pd.DataFrame(
            [
                {
                    "nome": "Aluno",
                    "contrato": "Plano Inexistente",
                    "cpf": "12345678901",
                    "status": "Ativo",
                    "data_de_nascimento": datetime(2000, 1, 1),
                    "data_de_cadastro": 5,
                }
            ]
        )
        file = SimpleUploadedFile("data.csv", b"content")
        with patch("core.uploadfile.pd.read_csv", return_value=df):
            response = upload_file(file)
        self.assertEqual(response["status_code"], "422")

    def test_upload_file_csv_success(self):
        df = pd.DataFrame(
            [
                {
                    "nome": "Aluno",
                    "contrato": self.plan.name_plan,
                    "cpf": "12345678901",
                    "status": "Ativo",
                    "data_de_nascimento": datetime(2000, 1, 1),
                    "data_de_cadastro": 5,
                }
            ]
        )
        file = SimpleUploadedFile("data.csv", b"content")
        with patch("core.uploadfile.pd.read_csv", return_value=df):
            response = upload_file(file)
        self.assertEqual(response["status_code"], "201")
        self.assertEqual(Student.objects.count(), 1)
        self.assertEqual(MonthlyFee.objects.count(), 1)

    def test_upload_file_xlsx_success(self):
        df = pd.DataFrame(
            [
                {
                    "nome": "Aluno",
                    "contrato": self.plan.name_plan,
                    "cpf": "12345678901",
                    "status": "Ativo",
                    "data_de_nascimento": datetime(2000, 1, 1),
                    "data_de_cadastro": 5,
                }
            ]
        )
        file = SimpleUploadedFile("data.xlsx", b"content")
        with patch("core.uploadfile.pd.read_excel", return_value=df):
            response = upload_file(file)
        self.assertEqual(response["status_code"], "201")
