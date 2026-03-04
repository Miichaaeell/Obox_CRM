# enterprise/admin.py
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


@admin.register(Enterprise)
class EnterpriseAdmin(admin.ModelAdmin):
    list_display = ()
    search_fields = ("id", "name")
    list_filter = ("created_at",)  # se created_at for DateTimeField/DateField
    date_hierarchy = "created_at"


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ("id", "created_at")
    search_fields = ("id",)
    list_filter = ("created_at",)
    date_hierarchy = "created_at"


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ("id",)
    search_fields = ("id",)
    list_filter = ()


@admin.register(StatusBill)
class StatusBillAdmin(admin.ModelAdmin):
    list_display = ("id",)
    search_fields = ("id",)


@admin.register(TypeBill)
class TypeBillAdmin(admin.ModelAdmin):
    list_display = ("id",)
    search_fields = ("id",)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("id", "created_at")
    search_fields = ("id",)
    list_filter = ("created_at",)
    date_hierarchy = "created_at"


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    # Colunas úteis na listagem
    list_display = (
        "id",
        "created_at",
    )
    # Navegação por data (escolha 1 campo principal)
    date_hierarchy = "created_at"  # ou "due_date" se fizer mais sentido

    # Busca: id, nome e campos relacionados
    search_fields = (
        "id",
        "payment_method__id",
        "payment_method__name",
    )

    # Performance: se você exibe FKs no list_display
    list_select_related = (
        "enterprise",
        "plan",
        "type_bill",
        "status",
        "payment_method",
    )

    ordering = ("-created_at",)

    # (Opcional) Se quiser busca mais “inteligente” por id digitado como texto
    def get_search_results(self, request, queryset, search_term):
        qs, use_distinct = super().get_search_results(request, queryset, search_term)
        term = search_term.strip()

        if term.isdigit():
            qs = qs | queryset.filter(id=int(term))

        return qs, use_distinct


@admin.register(Installments)
class InstallmentsAdmin(admin.ModelAdmin):
    list_display = ("id",)
    search_fields = ("id",)


@admin.register(NFSe)
class NFSeAdmin(admin.ModelAdmin):
    list_display = ("id",)
    search_fields = ("id",)


@admin.register(Cashier)
class CashierAdmin(admin.ModelAdmin):
    list_display = ("id",)
