from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q

from .models import Car, CarType, Schedule, Notification, CarReview, CustomUser
from .forms import CarForm, UserUpdateForm, ReviewForm

import os
import pdfkit
from datetime import datetime


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('car_type_list')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'login.html')


def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        if password == confirm_password:
            if CustomUser.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists')
            elif CustomUser.objects.filter(email=email).exists():
                messages.error(request, 'Email already exists')
            else:
                user = CustomUser.objects.create_user(username=username, email=email, password=password)
                user.save()
                messages.success(request, 'Account created successfully')
                return redirect('login')
        else:
            messages.error(request, 'Passwords do not match')
    return render(request, 'register.html')


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def profile_view(request):
    return render(request, 'profile.html', {'user': request.user})


@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'โปรไฟล์ถูกอัปเดตเรียบร้อยแล้ว!')
            return redirect('profile')
    else:
        form = UserUpdateForm(instance=request.user) 
    return render(request, 'edit_profile.html', {'form': form})


@staff_member_required 
def user_management(request):
    users = CustomUser.objects.all()
    return render(request, 'user_management.html', {'users': users})


@staff_member_required
def delete_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id) 
    if user.is_staff:
        messages.error(request, "ไม่สามารถลบผู้ดูแลระบบได้")
    else:
        user.delete()
        messages.success(request, "ลบผู้ใช้งานเรียบร้อยแล้ว")
    return redirect('user_management')


def is_admin(user):
    return user.is_staff


@user_passes_test(is_admin)
def car_pending_list(request, template_name='pending_car_list.html'):
    pending_cars = Car.objects.filter(status='Pending')
    return render(request, template_name, {'cars': pending_cars})


@user_passes_test(is_admin)
def approve_car(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    car.status = 'Approved'
    car.save()
    messages.success(request, "รถได้รับการอนุมัติเรียบร้อยแล้ว!")
    return redirect('car_list_by_type', type_id=car.car_type.id)


def welcome_view(request):
    return render(request, 'welcome.html')


def car_type_list_view(request):
    car_types = CarType.objects.all()
    return render(request, 'car_type_list.html', {'car_types': car_types})


def car_list_view(request):
    cars = Car.objects.all()
    return render(request, 'car_list.html', {'cars': cars})


def car_list_by_type(request, type_id):
    car_type = get_object_or_404(CarType, id=type_id)
    cars = Car.objects.filter(car_type=car_type, status='Approved').exclude(image__isnull=True, image='')
    return render(request, 'car_list.html', {'cars': cars, 'car_type': car_type})



def car_detail_view(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    owner = car.owner  
    context = {
        'car': car,
        'owner': owner, 
    }
    return render(request, 'car_detail.html', context)


@login_required
def my_cars(request):
    cars = Car.objects.filter(owner=request.user)
    if not cars:
        messages.info(request, "คุณยังไม่มีรถในระบบ")
    return render(request, 'my_cars.html', {'cars': cars})


@login_required
def add_car(request, type_id):
    car_type = get_object_or_404(CarType, id=type_id)
    if request.method == 'POST':
        form = CarForm(request.POST, request.FILES)
        if form.is_valid():
            car = form.save(commit=False)
            car.car_type = car_type
            car.owner = request.user
            car.status = 'Pending'
            car.save()
            messages.success(request, "รถของคุณถูกเพิ่มเรียบร้อยแล้ว! กรุณารอการอนุมัติ")
            return redirect('my_cars')
        else:
            # การแสดงข้อผิดพลาดใน log
            print(form.errors)
            messages.error(request, "กรุณาตรวจสอบข้อมูลที่กรอกให้ครบถ้วน")
    else:
        form = CarForm()
    
    return render(request, 'addcar.html', {'form': form, 'car_type': car_type})



@login_required
def edicar(request, id, type_id):
    car = get_object_or_404(Car, id=id)
    if request.user != car.owner and not request.user.is_staff:
        return HttpResponseForbidden("คุณไม่มีสิทธิ์ในการแก้ไขรถคันนี้")
    if request.method == 'POST':
        form = CarForm(request.POST, instance=car)
        if form.is_valid():
            form.save()
            messages.success(request, "แก้ไขข้อมูลรถสำเร็จ!")
            return redirect('car_list_by_type', type_id=type_id)
    else:
        form = CarForm(instance=car)
    return render(request, 'edit_car.html', {'form': form, 'car': car})


@login_required
def delete_car(request, car_id, type_id=None, json_response=False):
    car = get_object_or_404(Car, id=car_id)
    if request.user != car.owner and not request.user.is_staff:
        if json_response:
            return JsonResponse({'success': False, 'error': "คุณไม่มีสิทธิ์ลบรถคันนี้"}, status=403)
        messages.error(request, "คุณไม่มีสิทธิ์ลบรถคันนี้")
        return redirect('car_list')

    car_type_id = car.car_type.id
    car.delete()

    if json_response:
        return JsonResponse({'success': True, 'redirect_url': f'/cars/type/{car_type_id}/'})
    return redirect('car_list_by_type', type_id=type_id) if type_id else redirect('car_list')


def toggle_car_status(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    if car.owner == request.user:
        car.is_available = not car.is_available
        car.save()
    return redirect('car_detail', car_id=car.id)


@login_required
def car_schedule(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    schedules = Schedule.objects.filter(car=car).order_by('-date')
    
    return render(request, 'car_schedule.html', {'car': car, 'schedules': schedules})



def confirm_selection(request):
    selected_date = request.GET.get('date')
    selected_time = request.GET.get('time')
    car_id = request.GET.get('car_id')
    if selected_date and selected_time and car_id:
        car = Car.objects.get(id=car_id)
        return render(request, 'confirm_selection.html', {
            'selected_date': selected_date,
            'selected_time': selected_time,
            'car': car,
        })
    else:
        return render(request, 'error.html', {'message': 'ข้อมูลไม่ครบถ้วน'})


@login_required
def create_booking(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    if request.method == 'POST':
        selected_date = request.POST.get('date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        time_type = request.POST.get('time_type')

        if not selected_date:
            messages.error(request, "กรุณาเลือกวันที่")
            return redirect('book_time', car_id=car.id)
      
        if not time_type and (not start_time or not end_time):
            messages.error(request, "กรุณาเลือกช่วงเวลาให้ครบถ้วน")
            return redirect('book_time', car_id=car.id)

        if time_type == "morning":
            start_time = "08:00"
            end_time = "12:00"
        elif time_type == "afternoon":
            start_time = "13:00"
            end_time = "17:00"
        elif start_time and end_time:
            time_type = "custom"
        else:
            messages.error(request, "กรุณาเลือกช่วงเวลาให้ครบถ้วน")
            return redirect('book_time', car_id=car.id)

        if Schedule.objects.filter(car=car, date=selected_date, start_time__lt=end_time, end_time__gt=start_time).exists():
            messages.error(request, "ช่วงเวลานี้ถูกจองแล้ว กรุณาเลือกช่วงเวลาอื่น")
            return redirect('book_time', car_id=car.id)

        try:
            schedule = Schedule.objects.create(
                car=car,
                date=selected_date,
                start_time=start_time,
                end_time=end_time,
                time=time_type,  
                is_booked=False,
                booked_by=request.user
            )

            Notification.objects.create(
                user=car.owner,
                borrower=request.user,
                message=f"🚗 คุณมีการจองรถ {car.name} จาก {request.user.username} วันที่ {selected_date} ช่วง {start_time} ถึง {end_time} รอการอนุมัติ",
                schedule=schedule,
                is_confirmed=False,
                is_approved=False
            )
            
            Notification.objects.create(
                user=request.user,  
                message=f"🕒 คุณได้ส่งคำขอจองรถ {car.name} วันที่ {selected_date} ช่วง {start_time} ถึง {end_time} รอการอนุมัติจากเจ้าของรถ",
                schedule=schedule,
                is_confirmed=False,
                is_approved=False
            )

            messages.success(request, "📢 การจองของคุณถูกส่งแล้ว! รอเจ้าของรถอนุมัติ")
            return redirect('notification_list')

        except Exception as e:
            messages.error(request, f"เกิดข้อผิดพลาดในการจอง: {str(e)}")
            return redirect('car_detail', car_id=car.id)

    return redirect('car_detail', car_id=car.id)



def get_available_slots(car, selected_date):
    booked_slots = Schedule.objects.filter(car=car, date=selected_date, is_booked=True).values_list("start_time", "end_time")
    time_slots = [{"start": f"{hour}:00", "end": f"{hour+1}:00"} for hour in range(8, 18)]
    
    return [
        {
            "start": slot["start"], 
            "end": slot["end"],
            "booked": any(start == slot["start"] and end == slot["end"] for start, end in booked_slots)
        }
        for slot in time_slots
    ]

def book_time(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    selected_date = request.GET.get('date', None)
    available_slots = get_available_slots(car, selected_date)

    return render(request, 'book_time.html', {
        'car': car,
        'available_slots': available_slots,
        'selected_date': selected_date
    })


@login_required
def user_reservations(request):
    reservations = Schedule.objects.filter(booked_by=request.user)
    return render(request, 'user_reservations.html', {'reservations': reservations})


@login_required
def cancel_reservation(request, reservation_id):
    reservation = get_object_or_404(Schedule, id=reservation_id, booked_by=request.user)
    if reservation.is_booked:
        reservation.is_booked = False
        reservation.booked_by = None
        reservation.save()

        Notification.objects.create(
            user=reservation.car.owner,
            message=f"🚨 การจองรถ {reservation.car.name} วันที่ {reservation.date} ของ {request.user.username} ถูกยกเลิกแล้ว",
            schedule=reservation,
            is_confirmed=True,
            is_approved=False
        )

        Notification.objects.create(
            user=request.user,
            message=f"🚨 การจองรถ {reservation.car.name} วันที่ {reservation.date} ถูกยกเลิกแล้ว",
            schedule=reservation,
            is_confirmed=True,
            is_approved=False
        )

        messages.success(request, "ยกเลิกการจองสำเร็จ")
    else:
        messages.error(request, "ไม่สามารถยกเลิกการจองนี้ได้")
    return redirect('user_reservations')


@login_required
def confirm_reservation(request, schedule_id):
    schedule = get_object_or_404(Schedule, id=schedule_id)

    if request.method == 'POST':
        action = request.POST.get('action')
        is_approved = action == 'approve'
        
        # อัปเดตสถานะการจอง
        schedule.is_booked = is_approved
        schedule.is_confirmed = True  # เปลี่ยนสถานะการยืนยัน
        schedule.save()

        # อัปเดตการแจ้งเตือนเดิมทั้งหมดที่เกี่ยวข้องกับตารางงานนี้
        Notification.objects.filter(schedule=schedule).update(
            is_confirmed=True, 
            is_approved=is_approved
        )

        # สร้างการแจ้งเตือนใหม่เพื่อแจ้งผลลัพธ์
        message = f"การจองรถ {schedule.car.name} วันที่ {schedule.date} ได้รับการ{'อนุมัติ' if is_approved else 'ปฏิเสธ'}"
        Notification.objects.create(
            user=schedule.booked_by, 
            message=message, 
            schedule=schedule, 
            is_confirmed=True, 
            is_approved=is_approved
        )

        # รีเฟรชหน้าแจ้งเตือนหลังจากการอัปเดต
        return redirect('notification_list')

    return HttpResponseForbidden()


@login_required
def notification_list(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-timestamp')
    grouped_notifications = []
    grouped = notifications.values('schedule__car__name', 'schedule__date').distinct()

    for group in grouped:
        car_name = group['schedule__car__name']
        date = group['schedule__date']
        
        group_notifications = notifications.filter(
            schedule__car__name=car_name,
            schedule__date=date
        )
        
        first_notification = group_notifications.first()
        if first_notification and first_notification.schedule:
            grouped_notifications.append({
                'car': first_notification.schedule.car, 
                'date': date,
                'notifications': group_notifications
            })

    return render(request, 'notification_list.html', {'grouped_notifications': grouped_notifications})


@login_required
def car_review_view(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    reviews = CarReview.objects.filter(car=car).order_by('-created_at')

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            if CarReview.objects.filter(car=car, user=request.user).exists():
                messages.error(request, "คุณได้รีวิวรถคันนี้ไปแล้ว")
                return redirect('car_review', car_id=car.id)

            review = form.save(commit=False)
            review.car = car
            review.user = request.user
            review.save()

            messages.success(request, "เพิ่มรีวิวสำเร็จ!")

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': "เพิ่มรีวิวสำเร็จ!"})

            return redirect('car_review', car_id=car.id)
    else:
        form = ReviewForm()

    return render(request, 'car_review.html', {'car': car, 'reviews': reviews, 'form': form})


