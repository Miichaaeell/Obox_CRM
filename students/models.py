from django.db import models
from django.utils import timezone

from core.models import TimeStampedModel


class StatusStudent(TimeStampedModel, models.Model):
    status = models.CharField(max_length=100, verbose_name='Status do Aluno',
                              help_text='Enter the status of the student, e.g., Active, Inactive')

    def __str__(self):
        return self.status

    class Meta:
        verbose_name = 'Status do Aluno'
        verbose_name_plural = 'Status dos Alunos'


class Student(TimeStampedModel, models.Model):
    name = models.CharField(max_length=100, verbose_name='Nome Completo',
                            help_text='Enter the full name of the student')
    cpf_cnpj = models.CharField(
        max_length=18, unique=True, verbose_name='CPF/CNPJ', help_text='Enter a valid CPF or CNPJ number')
    date_of_birth = models.DateField(
        blank=True, null=True, verbose_name='Date of Birth')
    phone_number = models.CharField(max_length=20, blank=True, null=True,
                                    verbose_name='Número de telefone', help_text='Enter a valid phone number')
    status = models.ForeignKey(
        StatusStudent, on_delete=models.PROTECT, verbose_name='Status do Aluno')
    observation = models.TextField(
        verbose_name='Observação', help_text='Additional notes about the student')
    due_date = models.IntegerField(
        verbose_name='Data de Vencimento', help_text='Enter the due date for payments')
    plan = models.ForeignKey(
        'enterprise.Plan', on_delete=models.PROTECT, verbose_name='Plano',
        help_text='Select the plan associated with the student')

    class Meta:
        verbose_name = 'Student'
        verbose_name_plural = 'Students'
        ordering = ['status', 'name']

    def __str__(self):
        return f"{self.name}"


class Frequency(TimeStampedModel, models.Model):
    student = models.ForeignKey(
        Student, on_delete=models.PROTECT, verbose_name='Aluno', related_name='frequencies')
    attendance_date = models.DateField(
        verbose_name='Data da Frequência', default=timezone.localdate)

    def __str__(self):
        return f"{self.student.name} - {self.attendance_date}"

    class Meta:
        verbose_name = 'Frequência'
        verbose_name_plural = 'Frequências'
        ordering = ['-attendance_date', '-created_at']
        unique_together = ('student', 'attendance_date')


class History(TimeStampedModel, models.Model):
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, verbose_name='Aluno', related_name='histories')
    status = models.ForeignKey(
        StatusStudent, on_delete=models.PROTECT, verbose_name='Status do Aluno')
    description = models.TextField(
        verbose_name='Descrição', help_text='Descrição da ação realizada')

    def __str__(self):
        return f"{self.student.name} - {self.status.status}"

    class Meta:
        verbose_name = 'Histórico'
        verbose_name_plural = 'Históricos'
        ordering = ['-created_at']


class MonthlyFee(TimeStampedModel, models.Model):
    student = models.ForeignKey(
        Student, on_delete=models.SET_NULL, verbose_name='Aluno', related_name='monthly_fees', null=True)
    student_name = models.CharField(
        verbose_name='Nome do Aluno', max_length=124, null=True, blank=True)
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name='Valor da Mensalidade', help_text='Enter the monthly fee amount')
    due_date = models.DateField(
        verbose_name='Data de Vencimento', help_text='Enter the due date for the monthly fee')
    reference_month = models.CharField(
        max_length=7, help_text="Format MM/YYYY", verbose_name='Mês de Referência')
    paid = models.BooleanField(
        default=False, verbose_name='Pago', help_text='Indicates if the monthly fee has been paid')
    date_paid = models.DateField(verbose_name='Data que realizou o pagamento',
                                 help_text='Enter the paid date for the monthly fee', null=True, blank=True)
    discount_value = models.DecimalField(
        verbose_name='Valor de desconto', decimal_places=2, max_digits=10, default=0)
    discount_percent = models.DecimalField(
        verbose_name='Porcentagem de desconto', decimal_places=2, max_digits=5, default=0)
    plan = models.ForeignKey(
        'enterprise.Plan', on_delete=models.PROTECT, verbose_name='Plano', related_name='monthlyfees', null=True, blank=True)

    def __str__(self):
        return f"{self.student_name} - {self.amount} - {'Pago' if self.paid else 'Pendente'}"

    class Meta:
        verbose_name = 'Mensalidade'
        verbose_name_plural = 'Mensalidades'
        ordering = ['-created_at', 'student']


class Payment(TimeStampedModel, models.Model):
    montlhyfee = models.ForeignKey(
        MonthlyFee, on_delete=models.PROTECT, verbose_name='mensalidade', related_name='payments')
    payment_method = models.CharField(
        max_length=72, verbose_name='Metodo de pagamento')
    value = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name='Valor do pagamento')
    quantity_installments = models.IntegerField(
        verbose_name='Quantidade de parcelas', null=True, blank=True)
    cashier = models.ForeignKey(
        'enterprise.Cashier', on_delete=models.SET_NULL, blank=True, null=True, related_name='payments')

    def __str__(self):
        return f'Mensalidade {self.montlhyfee.student_name}'

    class Meta:
        verbose_name = 'Pagamento'
        verbose_name_plural = 'Pagamentos'
        ordering = ['-created_at']
