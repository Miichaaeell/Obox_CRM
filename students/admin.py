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


admin.site.register(StatusStudent)
admin.site.register(History)
admin.site.register(Frequency)
admin.site.register(MonthlyFee)
admin.site.register(Payment)
