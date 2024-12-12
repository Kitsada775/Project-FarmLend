from django.db import models

class CarType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Car(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    horsepower = models.IntegerField(verbose_name="แรงม้า", default= 0)
    car_type = models.ForeignKey(CarType, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='cars/', blank=True, null=True)

    def __str__(self):
        return self.name


class Schedule(models.Model):
    car = models.ForeignKey('Car', on_delete=models.CASCADE, related_name='schedules')
    date = models.DateField()
    is_booked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.car.name} - {self.date}"
    
