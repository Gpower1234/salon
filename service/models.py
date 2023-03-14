from django.db import models

# Create your models here.

class Braid(models.Model):
    name = models.CharField(max_length=50)
    duration = models.DurationField(default="00:00")
    price = models.PositiveIntegerField()

    def __str__(self):
        return self.name

    def formatted_work_time(self):
        days, hours, minutes = self.duration.seconds // 3600, (self.duration.seconds // 60) % 60, self.duration.seconds % 60
        duration_str = ''
        if hours:
            duration_str += f'{hours}hr '
        if minutes:
            duration_str += f'{minutes}min'
        return duration_str.strip()

class Crochet(models.Model):
    name = models.CharField(max_length=50)
    duration = models.DurationField(default="00:00")
    price = models.PositiveIntegerField()

    def __str__(self):
        return self.name

    def formatted_work_time(self):
        days, hours, minutes = self.duration.seconds // 3600, (self.duration.seconds // 60) % 60, self.duration.seconds % 60
        duration_str = ''
        if hours:
            duration_str += f'{hours}hr '
        if minutes:
            duration_str += f'{minutes}min'
        return duration_str.strip() 

class Twist(models.Model):
    name = models.CharField(max_length=50)
    duration= models.DurationField(default="00:00")
    price = models.PositiveIntegerField()

    def __str__(self):
        return self.name

    def formatted_work_time(self):
        days, hours, minutes = self.duration.seconds // 3600, (self.duration.seconds // 60) % 60, self.duration.seconds % 60
        duration_str = ''
        if hours:
            duration_str += f'{hours}hr '
        if minutes:
            duration_str += f'{minutes}min'
        return duration_str.strip()

class Natural_hair(models.Model):
    name = models.CharField(max_length=50)
    duration = models.DurationField(default="00:00")
    price = models.PositiveIntegerField()

    def __str__(self):
        return self.name

    def formatted_work_time(self):
        days, hours, minutes = self.duration.seconds // 3600, (self.duration.seconds // 60) % 60, self.duration.seconds % 60
        duration_str = ''
        if hours:
            duration_str += f'{hours}hr '
        if minutes:
            duration_str += f'{minutes}min'
        return duration_str.strip()

class Other_service(models.Model):
    name = models.CharField(max_length=50)
    duration = models.DurationField(default="00:00")
    price = models.PositiveIntegerField()

    def __str__(self):
        return self.name

    def formatted_work_time(self):
        days, hours, minutes = self.duration.seconds // 3600, (self.duration.seconds // 60) % 60, self.duration.seconds % 60
        duration_str = ''
        if hours:
            duration_str += f'{hours}hr '
        if minutes:
            duration_str += f'{minutes}min'
        return duration_str.strip()