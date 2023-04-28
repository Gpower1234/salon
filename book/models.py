from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
# Create your models here.


TIME_CHOICES = (
    ("8 AM", "8 AM"),
    ("2 PM", "2 PM"),
)

class Appointment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=225, blank=True, null=True)
    service = models.CharField(max_length=50)
    day = models.DateField(default=datetime.now)
    time = models.CharField(max_length=10, choices=TIME_CHOICES, default="8 AM")
    deposit = models.IntegerField(null=True)
    price = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    time_ordered = models.DateTimeField(default=datetime.now)
    update_count = models.IntegerField(default=0, null=False)

    def save(self, *args, **kwargs):
        if not self.user_id and self.name:
            self.name = self.name.strip() #Remove whitespace
            try:
                self.user = User.objects.get(username=self.name)
            except User.DoesNotExist:
                pass

        super().save(*args, **kwargs)

    
    def __str__(self):
        if self.user:
            return f"{self.user.username} | day: {self.day} | time: {self.time}"
        else:
            return f"{self.user.name} | day: {self.day} | time: {self.time}"


class LockDate(models.Model):
    date = models.DateField()

    def __str__(self):
        return f"{self.date}"



