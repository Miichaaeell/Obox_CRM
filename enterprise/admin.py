from django.contrib import admin

from enterprise.models import (
    Bill,
    Cashier,
    Enterprise,
    Installments,
    NFSe,
    PaymentMethod,
    Plan,
    Service,
    StatusBill,
    TypeBill,
)


admin.site.register(Enterprise)
admin.site.register(StatusBill)
admin.site.register(TypeBill)
admin.site.register(Bill)
admin.site.register(PaymentMethod)
admin.site.register(NFSe)
admin.site.register(Cashier)
admin.site.register(Plan)
admin.site.register(Installments)
admin.site.register(Service)
