from django.db import models
from core.models import TimeStampedModel
from enterprise.models import PaymentMethod


class Product(TimeStampedModel, models.Model):
    name = models.CharField(max_length=255, verbose_name='Nome do produto')
    description = models.TextField(
        blank=True, null=True, verbose_name='Descrição do produto')
    price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name='Preço do produto')

    def __str__(self):
        return f'{self.name} - {self.price}'
    
    class Meta:
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'
        ordering = ['name']

class ProductStock(TimeStampedModel, models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name='stocks', verbose_name='Produto')
    quantity = models.PositiveIntegerField(verbose_name='Quantidade em estoque')

    def __str__(self):
        return f'{self.product.name} - {self.quantity} em estoque'
    
    class Meta:
        verbose_name = 'Estoque do Produto'
        verbose_name_plural = 'Estoques dos Produtos'
        ordering = ['product__name']
        

class Intflow(TimeStampedModel, models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name='intflows', verbose_name='Produto')
    quantity = models.PositiveIntegerField(verbose_name='Quantidade de entrada')
    description = models.TextField(
        blank=True, null=True, verbose_name='Descrição da movimentação')

    def __str__(self):
        return f'{self.product.name} - {self.quantity}'
    
    class Meta:
        verbose_name = 'Entrada de Estoque'
        verbose_name_plural = 'Entradas de Estoque'
        ordering = ['-created_at']
        
        
class Sale(TimeStampedModel, models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name='sales', verbose_name='Produto')
    value_unitary = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name='Valor unitário do produto')
    quantity = models.PositiveIntegerField(verbose_name='Quantidade vendida')
    discount_value = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00, verbose_name='Desconto aplicado')
    discount_percent = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00, verbose_name='Percentual de desconto aplicado')
    total_price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name='Preço total da venda')
    payment_method = models.ForeignKey(
        PaymentMethod, on_delete=models.PROTECT, related_name='sales', verbose_name='Método de pagamento')

    def __str__(self):
        return f'Venda de {self.quantity} x {self.product.name} - Total: {self.total_price}'
    
    class Meta:
        verbose_name = 'Venda'
        verbose_name_plural = 'Vendas'
        ordering = ['-created_at']