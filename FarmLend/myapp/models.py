from django.db import models
from django import forms
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.conf import settings


class CarType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Car(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
    ]
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    horsepower = models.IntegerField(verbose_name="แรงม้า", default= 0)
    car_type = models.ForeignKey(CarType, related_name='cars', on_delete=models.CASCADE)  # เพิ่ม related_name ที่นี่
    image = models.ImageField(upload_to='cars/', blank=True, null=True, default='default_car.jpg')
    status = models.CharField(max_length=20, choices=[('Approved', 'Approved'), ('Pending', 'Pending')])
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)  # Owner field
    is_available = models.BooleanField(default=True)  # สถานะของรถ (พร้อมใช้งานหรือไม่)
    
    def __str__(self):
        return self.name

class Schedule(models.Model):
    car = models.ForeignKey('myapp.Car', on_delete=models.CASCADE, related_name='schedules')
    date = models.DateField()
    is_booked = models.BooleanField(default=False)
    time = models.CharField(max_length=20, choices=[('morning', 'ช่วงเช้า'), ('afternoon', 'ช่วงบ่าย')] , default= 0 )  # ช่วงเวลา

    def __str__(self):
        return f"{self.car.name} - {self.date} ({self.time})"
    

class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ['name', 'description', 'horsepower', 'image']



class CustomUser(AbstractUser):
    nickname = models.CharField(max_length=50, null=True, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)

    # Add related_name to resolve clashes
    groups = models.ManyToManyField(
        Group,
        related_name='customuser_groups',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )

    def __str__(self):
        return self.username


