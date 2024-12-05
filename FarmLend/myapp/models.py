from django.db import models

class CarType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Car(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    horsepower = models.IntegerField()
    image = models.ImageField(upload_to='car_images/', null=True, blank=True)
    car_type = models.ForeignKey(CarType, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
