from django.contrib import admin

from students.models import (
    Frequency,
    History,
    MonthlyFee,
    StatusStudent,
    Student,
    Payment,
)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("id", "name")
    list_filter = ("created_at",)  # se created_at for DateTimeField/DateField
    date_hierarchy = "created_at"


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    search_fields = ["montlhyfee__student__name"]
    list_filter = ["payment_method"]


@admin.register(MonthlyFee)
class MonthlyFeeAdmin(admin.ModelAdmin):
    search_fields = ["student_name", "reference_month", "plan"]
    list_filter = ["plan", "reference_month"]


admin.site.register(StatusStudent)
admin.site.register(History)
admin.site.register(Frequency)
