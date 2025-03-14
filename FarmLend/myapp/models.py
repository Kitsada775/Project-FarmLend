from django.db import models
from django import forms
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.conf import settings
from django.contrib.auth.models import User

class CarType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Car(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
    ]

    PRICING_TYPE_CHOICES = [
        ('flat', 'ราคาเหมา'),
        ('per_rai', 'ราคาต่อไร่')
    ]

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    horsepower = models.IntegerField(verbose_name="แรงม้า", default=0)
    car_type = models.ForeignKey(CarType, related_name='cars', on_delete=models.CASCADE) 
    image = models.ImageField(upload_to='cars/', blank=True, null=True, default='default_car.jpg')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='cars')    
    is_available = models.BooleanField(default=True)  
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    morning_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="ราคาเหมา ช่วงเช้า")
    morning_custom_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="ราคาที่กำหนดเอง ช่วงเช้า")
    afternoon_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="ราคาเหมา ช่วงบ่าย")
    afternoon_custom_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="ราคาที่กำหนดเอง ช่วงบ่าย")

    price_per_rai = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="ราคาต่อไร่")
    time_per_rai = models.IntegerField(null=True, blank=True, verbose_name="เวลาทำงานต่อไร่ (นาที)")
    contact_owner = models.BooleanField(default=False, verbose_name="ต้องการให้ติดต่อเจ้าของรถ")

    def __str__(self):
        return self.name


class Schedule(models.Model):
    TIME_CHOICES = [
        ('morning', 'ช่วงเช้า'),
        ('afternoon', 'ช่วงบ่าย'),
        ('custom', 'กำหนดเอง')
    ]

    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='schedules')
    date = models.DateField()  # วันที่จอง
    start_time = models.TimeField(null=True, blank=True)  # เวลาเริ่มต้น
    end_time = models.TimeField(null=True, blank=True)  # เวลาสิ้นสุด
    time = models.CharField(max_length=20, choices=TIME_CHOICES, null=True, blank=True)  # เลือกช่วงเวลา
    is_booked = models.BooleanField(default=False)  # ตรวจสอบว่าถูกจองแล้วหรือยัง
    booked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # เชื่อมกับผู้ใช้ที่ทำการจอง
        on_delete=models.CASCADE,
        related_name='bookings',
        null=True, blank=True  # อนุญาตให้ว่างได้สำหรับการจองที่ยังไม่มีเจ้าของ
    )

    def __str__(self):
        if self.time == 'morning':
            return f"{self.car.name} - {self.date} (ช่วงเช้า 08:00 - 12:00)"
        elif self.time == 'afternoon':
            return f"{self.car.name} - {self.date} (ช่วงบ่าย 13:00 - 17:00)"
        return f"{self.car.name} - {self.date} ({self.start_time} to {self.end_time})"
   

class CustomUser(AbstractUser):
    nickname = models.CharField(max_length=50, null=True, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

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


class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # ผู้ที่ได้รับการแจ้งเตือน
    borrower = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='borrower_notifications', null=True, blank=True)
    message = models.TextField()  # ข้อความแจ้งเตือน
    timestamp = models.DateTimeField(auto_now_add=True)  # เวลาที่แจ้งเตือนถูกสร้าง
    schedule = models.ForeignKey(Schedule, null=True, blank=True, on_delete=models.SET_NULL)  # เชื่อมโยงกับการจอง
    is_confirmed = models.BooleanField(default=False)  # สถานะการยืนยันการจอง
    is_approved = models.BooleanField(default=False)  # สถานะการอนุมัติจอง

    def __str__(self):
        return f"Notification for {self.user.username} at {self.timestamp}"

class CarReview(models.Model):
    car = models.ForeignKey('Car', on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], null=True, blank=True)  # ให้ rating เป็น optional
    review_text = models.TextField(null=True, blank=True)  # ให้คอมเมนต์เป็น optional
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.car.name} by {self.user.username} ({'Rated' if self.rating else 'Comment'})"

