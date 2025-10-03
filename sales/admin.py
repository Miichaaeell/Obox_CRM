from django.contrib import admin

from sales.models import Intflow, Product, ProductStock, Sale


admin.site.register(Sale)
admin.site.register(Product)
admin.site.register(ProductStock)
admin.site.register(Intflow)
