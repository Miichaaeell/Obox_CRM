from django.contrib import admin

from students.models import Frequency, History, MonthlyFee, StatusStudent, Student


admin.site.register(Student)
admin.site.register(StatusStudent)
admin.site.register(History)
admin.site.register(Frequency)
admin.site.register(MonthlyFee)
