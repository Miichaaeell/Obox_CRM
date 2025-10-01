from django.db import models
from core.models import TimeStampedModel
from students.models import Student


class Enterprise(TimeStampedModel, models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name='Nome')
    cnpj = models.CharField(
        unique=True, help_text="CNPJ must be a valid 14-digit number ex: 01.234.567/0008-91", max_length=14, verbose_name='CNPJ')
    cep = models.CharField(max_length=10, blank=True, null=True,
                           help_text="CEP must be a valid format ex: 12345-678", verbose_name='CEP')
    city = models.CharField(max_length=100, blank=True, null=True,
                            help_text="City name, ex: São Paulo", verbose_name='Cidade')
    state = models.CharField(max_length=2, blank=True, null=True,
                             help_text="State must be a valid 2-letter abbreviation ex: SP", verbose_name='Estado')
    street = models.CharField(max_length=255, blank=True, null=True,
                              help_text="Street name, number, ex: Av. Paulista, 1000", verbose_name='Rua')
    phone_number = models.CharField(max_length=20, blank=True, null=True,
                                    help_text="Phone number must be a valid format ex: (19) 91234-5678", verbose_name='Telefone')
    email = models.EmailField(
        blank=True, null=True, help_text="Email must be a valid email address ex: your@email.com")
    cnae_code = models.CharField(max_length=10, blank=True, null=True,
                                 help_text="CNAE code must be a valid format ex: 47.11-3-01", verbose_name='Código CNAE')
    service_code = models.CharField(max_length=255, blank=True, null=True,
                                    help_text="Description of the CNAE code", verbose_name='Código do serviço')
    description_service = models.TextField(
        help_text="Detailed description of the service", verbose_name='Descrição do serviço')

    class Meta:
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'
        ordering = ['name']

    def __str__(self):
        return self.name


class StatusBill(TimeStampedModel, models.Model):
    status = models.CharField(max_length=100)

    def __str__(self):
        return self.status

    class Meta:
        verbose_name = 'Status da Conta'
        verbose_name_plural = 'Status das Contas'


class TypeBill(TimeStampedModel, models.Model):
    type_bill = models.CharField(max_length=100)

    def __str__(self):
        return self.type_bill

    class Meta:
        verbose_name = 'Tipo de Conta'
        verbose_name_plural = 'Tipos de Conta'


class PaymentMethod(TimeStampedModel, models.Model):
    method = models.CharField(max_length=100, verbose_name='método')

    def __str__(self):
        return self.method

    class Meta:
        verbose_name = 'Método de Pagamento'
        verbose_name_plural = 'Métodos de Pagamento'


class Bill(TimeStampedModel, models.Model):
    description = models.CharField(max_length=255, verbose_name='Conta')
    value = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name='valor')
    due_date = models.DateField(verbose_name='data de vencimento')
    status = models.ForeignKey(
        StatusBill, on_delete=models.CASCADE, verbose_name='status', related_name='bills')
    payment_method = models.ForeignKey(
        PaymentMethod, on_delete=models.PROTECT, blank=True, null=True)
    appellant = models.BooleanField(verbose_name='Recorrente', default=False)
    date_payment = models.DateField(
        verbose_name='Data do pagamento', blank=True, null=True)
    apply_discount = models.BooleanField(
        verbose_name='aplicar desconto', default=False)
    value_discount = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name='Valor de desconto', default=0)
    percent_discount = models.DecimalField(
        max_digits=5, decimal_places=4, verbose_name='Porcentagem de desconto', default=0)
    value_fine = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name='Valor da desconmulta', default=0)
    percent_fine = models.DecimalField(
        max_digits=5, decimal_places=4, verbose_name='Porcentagem da multa', default=0)
    total_value = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name='valor', blank=True, null=True)

    def __str__(self):
        return self.description

    class Meta:
        verbose_name = 'Conta'
        verbose_name_plural = 'Contas'
        ordering = ['-due_date', 'description']


class Cashier(TimeStampedModel, models.Model):
    description = models.TextField(
        blank=True, null=True, verbose_name='descrição')
    balance = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name='saldo')

    def __str__(self):
        return self.balance

    class Meta:
        verbose_name = 'Caixa'
        verbose_name_plural = 'Caixas'
        ordering = ['-created_at']


class Plan(TimeStampedModel, models.Model):
    name_plan = models.CharField(
        max_length=100, unique=True, verbose_name='Nome do Plano')
    description = models.TextField(
        blank=True, null=True, verbose_name='Descrição')
    price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name='Preço')
    duration_months = models.PositiveIntegerField(
        verbose_name='Duração (meses)')

    def __str__(self):
        return self.name_plan

    class Meta:
        verbose_name = 'Plano'
        verbose_name_plural = 'Planos'
        ordering = ['price']


class NFSe(models.Model):
    student = models.ForeignKey(
        Student, on_delete=models.PROTECT, verbose_name='Aluno', related_name='nfses')
    issue_date = models.DateField(
        auto_now_add=True, verbose_name='Data de Emissão')
    uuid_nfse = models.CharField(
        max_length=100, unique=True, verbose_name='UUID da NFSe')
    link_pdf = models.URLField(
        max_length=200, blank=True, null=True, verbose_name='Link do PDF')
    link_xml = models.URLField(
        max_length=200, blank=True, null=True, verbose_name='Link do XML')
    reference_month = models.CharField(
        max_length=7, help_text="Format MM/YYYY", verbose_name='Mês de Referência')

    def __str__(self):
        return f'NFSe {self.uuid_nfse} - {self.student}'

    class Meta:
        verbose_name = 'Nota Fiscal de Serviço Eletrônica (NFSe)'
        verbose_name_plural = 'Notas Fiscais de Serviço Eletrônicas (NFSe)'
        ordering = ['-issue_date', 'student']


class Installments(models.Model):
    quantity_installments = models.IntegerField(
        verbose_name='Quantidade de Parcelas', help_text='Ex. 1')

    def __str__(self):
        return f'{self.quantity_installments}x'

    class Meta:
        verbose_name = 'Quantidade de parcela'
        verbose_name_plural = 'quantidade de parcelas'
        ordering = ['quantity_installments']
