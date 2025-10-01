from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Sale, ProductStock, Intflow


@receiver(post_save, sender=Intflow)
def register_stock_on_intflow(sender, instance, created, **kwargs):
    if created:
        if ProductStock.objects.filter(product=instance.product).exists():
            product_stock = ProductStock.objects.get(product=instance.product)
            product_stock.quantity += instance.quantity
            product_stock.save()
        else:
            ProductStock.objects.create(
                product=instance.product, quantity=instance.quantity)


@receiver(post_save, sender=Sale)
def update_stock_on_sale(sender, instance, created, **kwargs):
    if created:
        try:
            product_stock = ProductStock.objects.get(product=instance.product)
            if product_stock.quantity >= instance.quantity:
                product_stock.quantity -= instance.quantity
                product_stock.save()
            else:
                raise ValueError(
                    "Estoque insuficiente para completar a venda.")
        except ProductStock.DoesNotExist:
            raise ValueError("Estoque do produto não encontrado.")
