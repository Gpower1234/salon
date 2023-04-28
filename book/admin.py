from django.contrib import admin
from .models import Appointment, LockDate
# Register your models here.

class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['user_or_name', 'service',  'day', 'time', 'price', 'deposit', 'time_ordered']
    ordering = ['-day']
    readonly_fields = ['user', 'service',  'day', 'time', 'price', 'deposit', 'time_ordered']

    def user_or_name(self, obj):
        if obj.user:
            return obj.user.username
        else: 
            return obj.name
        
    user_or_name.short_description = 'User/Name'

admin.site.register(Appointment, AppointmentAdmin)
admin.site.register(LockDate)

