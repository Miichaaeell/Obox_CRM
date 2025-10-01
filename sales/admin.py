from django.contrib import admin
from .models import Sale, Product, ProductStock, Intflow

admin.site.register(Sale)
admin.site.register(Product)
admin.site.register(ProductStock)
admin.site.register(Intflow)
