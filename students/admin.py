from django.contrib import admin
from .models import Student, StatusStudent, History, Frequency, MonthlyFee

admin.site.register(Student)
admin.site.register(StatusStudent)
admin.site.register(History)
admin.site.register(Frequency)
admin.site.register(MonthlyFee)
