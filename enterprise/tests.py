from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from enterprise.models import PaymentMethod, Plan
from students.models import MonthlyFee, StatusStudent, Student


class MonthlyFeePaymentAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        User = get_user_model()
        self.user = User.objects.create_user(
            username='tester',
            password='strong-password-123'
        )
        self.client.force_authenticate(self.user)

        self.payment_method = PaymentMethod.objects.create(
            method='Pix',
            applies_to='students'
        )

        self.plan = Plan.objects.create(
            name_plan='Plano Premium',
            description='Plano mensal',
            price=Decimal('100.00'),
            duration_months=12
        )

        self.status_active = StatusStudent.objects.create(status='Ativo')
        self.status_inactive = StatusStudent.objects.create(status='Inativo')

        self.student = Student.objects.create(
            name='Aluno Teste',
            cpf_cnpj='12345678901',
            date_of_birth=date(2000, 1, 1),
            phone_number='11999999999',
            status=self.status_active,
            observation='Teste automatizado',
            due_date=5,
            plan=self.plan
        )

        self.monthly_fee = MonthlyFee.objects.create(
            student=self.student,
            amount=Decimal('100.00'),
            due_date=date.today(),
            reference_month='01/2024',
            paid=False,
            plan=self.plan
        )

    def test_retrieve_monthlyfee_detail(self):
        url = reverse('monthlyfee_detail_api', args=[self.monthly_fee.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        payload = response.json()

        self.assertEqual(payload['plan'], self.plan.name_plan)
        self.assertEqual(Decimal(payload['base_amount']), self.plan.price)
        self.assertEqual(Decimal(payload['final_amount']), self.monthly_fee.amount)
        self.assertIn('payment_methods', payload)
        self.assertTrue(
            any(method['id'] == self.payment_method.id for method in payload['payment_methods'])
        )

    def test_update_monthlyfee_with_discount(self):
        url = reverse('monthlyfee_update_api')
        response = self.client.post(
            url,
            {
                'monthlyfee_id': self.monthly_fee.id,
                'payment_method': self.payment_method.id,
                'discount_percent': '10.00',
                'discount_value': '10.00',
                'final_amount': '90.00',
                'quantity_installments': 1,
            },
            format='json'
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertTrue(data.get('success'))
        payment = data.get('payment', {})
        self.assertEqual(Decimal(payment.get('final_amount')), Decimal('90.00'))

        self.monthly_fee.refresh_from_db()
        self.assertTrue(self.monthly_fee.paid)
        self.assertEqual(self.monthly_fee.payment_method, 'PIX')
        self.assertEqual(self.monthly_fee.discount_percent, Decimal('10.00'))
        self.assertEqual(self.monthly_fee.discount_value, Decimal('10.00'))
        self.assertEqual(self.monthly_fee.amount, Decimal('90.00'))
        self.assertEqual(self.monthly_fee.quantity_installments, 1)

    def test_inactivate_student_requires_reason(self):
        url = reverse('student_inactivate_api')
        response = self.client.post(
            url,
            {
                'student_id': self.student.id,
                'reason': '   ',
            },
            format='json'
        )

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data.get('success'))
        self.assertIn('reason', data.get('errors', {}))

    def test_inactivate_student_success(self):
        MonthlyFee.objects.create(
            student=self.student,
            amount=Decimal('80.00'),
            due_date=date.today(),
            reference_month='02/2024',
            paid=False,
            plan=self.plan
        )
        MonthlyFee.objects.create(
            student=self.student,
            amount=Decimal('75.00'),
            due_date=date.today(),
            reference_month='03/2024',
            paid=True,
            plan=self.plan
        )

        url = reverse('student_inactivate_api')
        response = self.client.post(
            url,
            {
                'student_id': self.student.id,
                'reason': 'Aluno solicitou suspensão.',
            },
            format='json'
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get('success'))
        self.assertIn('message', data)

        self.student.refresh_from_db()
        self.assertEqual(self.student.status, self.status_inactive)
        self.assertEqual(self.student.observation, 'Aluno solicitou suspensão.')

        remaining_fees = MonthlyFee.objects.filter(student=self.student)
        self.assertEqual(remaining_fees.count(), 1)
        self.assertTrue(all(fee.paid for fee in remaining_fees))
