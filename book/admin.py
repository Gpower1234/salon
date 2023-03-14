from django.contrib import admin
from .models import Appointment, LockDate
# Register your models here.

class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'service',  'day', 'time', 'price', 'deposit', 'time_ordered']
    ordering = ['-day']
    readonly_fields = ['user', 'service',  'day', 'time', 'price', 'deposit', 'time_ordered']

admin.site.register(Appointment, AppointmentAdmin)
admin.site.register(LockDate)

