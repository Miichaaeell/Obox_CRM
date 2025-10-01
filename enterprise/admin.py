from django.contrib import admin
from .models import Enterprise, StatusBill, TypeBill, Bill, PaymentMethod, Cashier, Plan, NFSe, Installments

admin.site.register(Enterprise)
admin.site.register(StatusBill)
admin.site.register(TypeBill)
admin.site.register(Bill)
admin.site.register(PaymentMethod)
admin.site.register(NFSe)
admin.site.register(Cashier)
admin.site.register(Plan)
admin.site.register(Installments)
