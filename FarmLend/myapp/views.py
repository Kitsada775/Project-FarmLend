from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import *
from django.http import HttpResponseForbidden
from django.urls import reverse
from .forms import CarForm, UserUpdateForm
from django.contrib.auth.decorators import user_passes_test, login_required
from django.http import JsonResponse
from .models import Car, Notification, Schedule
from datetime import datetime
from django.contrib.admin.views.decorators import staff_member_required
from myapp.models import CustomUser
from django.db.models import Q
from .models import Car, Review
from .forms import ReviewForm


import os
import pdfkit
from django.http import HttpResponse

# กำหนด path ของ wkhtmltopdf (Windows ใช้ path นี้, Linux/Mac อาจไม่ต้อง)
PDFKIT_CONFIG = pdfkit.configuration(wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")

def app_to_pdf(request, app_name):
    app_path = os.path.join(settings.BASE_DIR, app_name)
    pdf_filename = f"{app_name}.pdf"

    if not os.path.exists(app_path):
        return HttpResponse("App not found", status=404)

    html_content = f"<h1>Source Code of App: {app_name}</h1>"

    for root, dirs, files in os.walk(app_path):
        for file in files:
            if file.endswith((".py", ".html", ".css", ".js")):  # แปลงเฉพาะไฟล์ที่ต้องการ
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:  # ✅ อ่านไฟล์เป็น UTF-8
                    html_content += f"<h2>{file}</h2><pre>{f.read()}</pre>"

    # ✅ ใช้ pdfkit พร้อมกำหนดให้ใช้ encoding UTF-8
    options = {'encoding': 'UTF-8'}
    pdfkit.from_string(html_content, pdf_filename, configuration=PDFKIT_CONFIG, options=options)

    with open(pdf_filename, "rb") as pdf:
        response = HttpResponse(pdf.read(), content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{pdf_filename}"'
        return response


@staff_member_required  # ให้เฉพาะแอดมินเข้าถึงได้
def user_management(request):
    users = User.objects.all()
    return render(request, 'user_management.html', {'users': users})

@staff_member_required
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if user.is_staff:
        messages.error(request, "ไม่สามารถลบผู้ดูแลระบบได้")
    else:
        user.delete()
        messages.success(request, "ลบผู้ใช้งานเรียบร้อยแล้ว")

    return redirect('user_management')


# ฟังก์ชันสำหรับหน้าแรก
def welcome_view(request):
    """
    แสดงหน้า Welcome (หน้าแรกของระบบ)
    """
    return render(request, 'welcome.html')

# ฟังก์ชันสำหรับหน้าล็อกอิน
def login_view(request):
    """
    จัดการการเข้าสู่ระบบของผู้ใช้:
    - รับ username และ password
    - ตรวจสอบว่าถูกต้องหรือไม่
    - หากสำเร็จ จะเปลี่ยนไปยังหน้า car_type_list
    """
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

# ฟังก์ชันสำหรับหน้าสมัคร
def register_view(request):
    """
    สมัครสมาชิกใหม่:
    - ตรวจสอบความถูกต้องของข้อมูล
    - สร้างผู้ใช้ใหม่
    - ส่งข้อความแจ้งเตือนความสำเร็จหรือข้อผิดพลาด
    """
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

# ฟังก์ชันสำหรับการล็อกเอาท์
def logout_view(request):
    """
    ออกจากระบบ:
    - เคลียร์ session ของผู้ใช้
    """
    logout(request)
    return redirect('login')

# ฟังก์ชันแสดงรายการประเภทของรถ
def car_type_list_view(request):
    """
    แสดงรายการประเภทของรถ
    """
    car_types = CarType.objects.all()
    return render(request, 'car_type_list.html', {'car_types': car_types})

# ฟังก์ชันแสดงรายการรถ
def car_list_view(request):
    cars = Car.objects.all()
    return render(request, 'car_list.html', {'cars': cars})

# ฟังก์ชันแสดงรถในแต่ละประเภท
def car_list_by_type(request, type_id):
    """
    แสดงรายการรถที่อยู่ในประเภทที่กำหนด
    """
    cars = Car.objects.filter(
        car_type_id=type_id, 
        status='Approved'
    ).exclude(image__isnull=True).exclude(image='')  # กรองรถที่ไม่มีไฟล์ภาพ
    return render(request, 'car_list.html', {'cars': cars, 'car_type': get_object_or_404(CarType, id=type_id)})

# ฟังก์ชันแสดงรายละเอียดของรถแต่ละคัน
def car_detail_view(request, car_id):
    """
    แสดงรายละเอียดของรถแต่ละคัน
    """
    car = get_object_or_404(Car, pk=car_id)
    return render(request, 'car_detail.html', {'car': car})

# ฟังก์ชันเพิ่มรถ
def add_car(request, type_id):
    car_type = get_object_or_404(CarType, id=type_id)  # ดึงข้อมูลประเภทของรถ
    if request.method == 'POST':
        form = CarForm(request.POST, request.FILES)
        if form.is_valid():
            car = form.save(commit=False)
            car.car_type = CarType.objects.get(id=request.POST.get('car_type'))  # ใช้ค่า car_type ที่มาจากฟอร์ม
            car.status = 'Pending'  # ตั้งสถานะเป็น 'Pending' สำหรับการอนุมัติ
            car.save()
            return redirect('car_list_by_type', type_id=car.car_type.id)  # รีไดเรกไปยังหน้ารายการรถของประเภทนั้น
    else:
        form = CarForm()

    return render(request, 'addcar.html', {'form': form, 'car_type': car_type})


# ฟังก์ชันแก้ไขรถ
from django.shortcuts import redirect

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


# ฟังก์ชันลบรถ
@login_required
def delcar(request, car_id, type_id):
    car = get_object_or_404(Car, id=car_id)

    # ตรวจสอบว่าเจ้าของรถหรือแอดมินหรือไม่
    if request.user != car.owner and not request.user.is_staff:
        return HttpResponseForbidden("คุณไม่มีสิทธิ์ในการลบรถคันนี้")

    # ถ้าเจ้าของหรือแอดมิน ยืนยันการลบ
    car.delete()
    return redirect('car_list')  # เปลี่ยนไปหน้าแสดงรายการรถ

# ฟังก์ชันแสดงตารางงานของรถ
def car_schedule(request, car_id):
    # กรองรายการที่ได้รับการยืนยันแล้ว
    schedules = Schedule.objects.filter(car_id=car_id, is_booked=True)

    return render(request, 'car_schedule.html', {'schedules': schedules})

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


# แสดงรายการรถที่รอการอนุมัติ
def car_approval_list(request):
    # ดึงเฉพาะรถที่รอการอนุมัติ
    cars_pending = Car.objects.filter(status='Pending')

    # ส่งข้อมูล car_type ไปพร้อมกับ cars
    return render(request, 'car_approval_list.html', {'cars': cars_pending})


# ฟังก์ชันสำหรับอนุมัติรถ
def approve_car(request, car_id):
    if not request.user.is_staff:
        return redirect('car_type_list')

    car = get_object_or_404(Car, id=car_id)
    car.status = 'Approved'  # อัปเดตสถานะเป็น Approved
    car.save()  # บันทึกการเปลี่ยนแปลง
    return redirect('car_list_by_type', type_id=car.car_type.id)  # กลับไปหน้ารายการรถ

# แสดงรายการรถที่อนุมัติแล้ว
def car_list_by_type_view(request, type_id):
    # ดึงข้อมูล CarType โดยใช้ type_id
    car_type = get_object_or_404(CarType, id=type_id)
    
    # ใช้ car_type.cars.all() เพื่อดึงรถทั้งหมดที่เกี่ยวข้องกับ car_type นี้
    cars = car_type.cars.filter(status='Approved').exclude(image__isnull=True).exclude(image='')

    return render(request, 'car_list.html', {'cars': cars, 'car_type': car_type})



def pending_car_list(request):
    cars = Car.objects.filter(status='Pending').exclude(image__isnull=True).exclude(image='')
    return render(request, 'pending_cars.html', {'cars': cars})

# เช็คว่า user เป็น staff (admin) หรือไม่
def is_admin(user):
    return user.is_staff

@user_passes_test(is_admin)
def pending_car_list(request):
    pending_cars = Car.objects.filter(status='Pending')  # รถที่ยังไม่ได้อนุมัติ
    return render(request, 'pending_car_list.html', {'cars': pending_cars})


@login_required
def delete_car(request, car_id):
    car = get_object_or_404(Car, id=car_id)

    # ตรวจสอบว่าเป็นเจ้าของรถหรือเป็นแอดมิน
    if request.user != car.owner and not request.user.is_staff:
        return JsonResponse({'success': False, 'error': "คุณไม่มีสิทธิ์ลบรถคันนี้"}, status=403)

    car_type_id = car.car_type.id  # ดึงประเภทของรถไว้ก่อนลบ
    car.delete()

    return JsonResponse({'success': True, 'redirect_url': f'/cars/type/{car_type_id}/'}) 


@login_required
def profile_view(request):
    user = CustomUser.objects.filter(id=request.user.id)
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

def car_detail_view(request, car_id):
    # ดึงข้อมูลรถตาม car_id
    car = get_object_or_404(Car, id=car_id)
    
    # ดึงข้อมูลเจ้าของรถ
    owner = car.owner  # เจ้าของรถ (ผู้ใช้)
    
    # ส่งข้อมูลไปที่เทมเพลต
    context = {
        'car': car,
        'owner': owner,  # ส่งข้อมูลเจ้าของรถไปที่เทมเพลต
    }

    return render(request, 'car_detail.html', context)

# ฟังก์ชันสำหรับเปลี่ยนสถานะของรถ
def toggle_car_status(request, car_id):
    # ดึงข้อมูลรถจากฐานข้อมูลโดยใช้ car_id
    car = get_object_or_404(Car, id=car_id)
    
    # ตรวจสอบว่าเจ้าของรถเป็นผู้ที่ล็อกอินอยู่หรือไม่
    if car.owner == request.user:
        # เปลี่ยนสถานะของรถ (พร้อมใช้งาน ↔ ไม่พร้อมใช้งาน)
        car.is_available = not car.is_available
        car.save()
    
    # หลังจากเปลี่ยนสถานะแล้ว ให้ย้อนกลับไปยังหน้ารายละเอียดของรถ
    return redirect('car_detail', car_id=car.id)

def my_cars(request):
    # ดึงข้อมูลรถที่เจ้าของเป็นผู้ใช้ปัจจุบัน
    cars = Car.objects.filter(owner=request.user)

    # ส่งข้อมูลรถไปยัง template
    return render(request, 'my_cars.html', {'cars': cars})

# ฟังก์ชันสำหรับการยืนยันการจอง
@login_required
def confirm_reservation(request, reservation_id):
    schedule = get_object_or_404(Schedule, id=reservation_id)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'approve':
            # อัพเดตสถานะให้เป็นยืนยัน
            schedule.is_booked = True
            schedule.save()

            # แจ้งเตือนผู้จองว่าการจองได้รับการยืนยัน
            Notification.objects.create(
                user=schedule.booked_by,
                message=f"เจ้าของรถ {schedule.car.name} ได้ยืนยันการจองของคุณ วันที่ {schedule.date} ช่วง {schedule.get_time_display()}",
                schedule=schedule,
                is_confirmed=True,
                is_approved=True
            )
        
        elif action == 'reject':
            # ลบการจองหากถูกปฏิเสธ
            schedule.delete()

            # แจ้งเตือนผู้จองว่าการจองถูกปฏิเสธ
            Notification.objects.create(
                user=schedule.booked_by,
                message=f"เจ้าของรถ {schedule.car.name} ปฏิเสธการจองของคุณ วันที่ {schedule.date} ช่วง {schedule.get_time_display()}",
                is_confirmed=True,
                is_approved=False
            )

        return redirect('notification_list')  # กลับไปที่แจ้งเตือน


# ฟังก์ชันการสร้างการจอง
@login_required
def create_booking(request, car_id):
    car = get_object_or_404(Car, id=car_id)

    if request.method == 'POST':
        selected_date = request.POST.get('date')
        selected_time = request.POST.get('time')

        if selected_date and selected_time:
            # ตรวจสอบว่าช่วงเวลานี้ถูกจองไปแล้วหรือไม่
            existing_booking = Schedule.objects.filter(car=car, date=selected_date, time=selected_time).exists()
            if existing_booking:
                messages.error(request, "ช่วงเวลานี้ถูกจองแล้ว กรุณาเลือกช่วงเวลาอื่น")
                return redirect('car_detail', car_id=car.id)

            # สร้างคำขอจองใหม่
            schedule = Schedule.objects.create(
                car=car,
                date=selected_date,
                time=selected_time,
                is_booked=False,  # ต้องให้เจ้าของรถกดยืนยันก่อน
                booked_by=request.user
            )

            Notification.objects.create(
                user=car.owner,  # เจ้าของรถ (ผู้รับการแจ้งเตือน)
                borrower=request.user,  # ผู้ยืม
                message=f"คุณมีการจองรถ {car.name} จาก {request.user.username} สำหรับวันที่ {selected_date} ช่วง {schedule.get_time_display()} โปรดตรวจสอบและอนุมัติ",
                schedule=schedule
            )

            messages.success(request, "ส่งคำขอจองไปยังเจ้าของรถแล้ว และคุณจะได้รับการแจ้งเตือนเมื่อมีการตอบกลับ")
            return redirect('notification_list')  # ไปยังหน้าการแจ้งเตือน
        else:
            messages.error(request, "กรุณาเลือกวันที่และช่วงเวลาให้ครบถ้วน")

    return render(request, 'book_time.html', {'car': car})


@login_required
def notification_list(request):
    # ดึงการแจ้งเตือนที่ผู้ใช้ได้รับ
    notifications_as_user = Notification.objects.filter(user=request.user).order_by('-timestamp')

    # ดึงการแจ้งเตือนที่ผู้ใช้เป็นผู้ยืม
    notifications_as_borrower = Notification.objects.filter(borrower=request.user).order_by('-timestamp')

    # รวมทั้งสองรายการ
    notifications = Notification.objects.filter(
        Q(user=request.user) |  # เจ้าของรถ
        Q(borrower=request.user)  # ผู้ยืม
    ).order_by('-timestamp')
    
    return render(request, 'notification_list.html', {
        'notifications': notifications,
        'is_owner': Car.objects.filter(owner=request.user).exists()  # เช็คว่าเป็นเจ้าของรถหรือไม่
    })


@login_required
def cancel_reservation(request, reservation_id):
    reservation = get_object_or_404(Schedule, id=reservation_id, booked_by=request.user)

    if reservation.is_booked:
        # ตั้งสถานะให้ว่าง
        reservation.is_booked = False
        reservation.booked_by = None
        reservation.save()

        # แจ้งเตือนเจ้าของรถ
        Notification.objects.create(
            user=reservation.car.owner,
            message=f"🚨 การจองรถ {reservation.car.name} วันที่ {reservation.date} ของ {request.user.username} ถูกยกเลิกแล้ว",
            schedule=reservation,
            is_confirmed=True,  # ถือว่าได้รับการยืนยันแล้ว
            is_approved=False   # แสดงว่าการจองถูกยกเลิก
        )

        # แจ้งเตือนผู้จองว่าการจองของพวกเขาถูกยกเลิก
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

    return redirect('user_reservations')  # กลับไปหน้ารายการจองของผู้ใช้


def car_review_view(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    reviews = CarReview.objects.filter(car=car)

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.car = car
            review.user = request.user  # กำหนดผู้ใช้ที่ส่งรีวิว
            review.save()
            return redirect('car_review', car_id=car.id)  # รีไดเร็กไปหน้ารีวิวหลังจากบันทึกเสร็จ

    else:
        form = ReviewForm()

    return render(request, 'car_review.html', {'car': car, 'reviews': reviews, 'form': form})


@staff_member_required  # ให้เฉพาะแอดมินเข้าถึงได้
def user_management(request):
    users = CustomUser.objects.all()  # ✅ เปลี่ยนจาก User.objects.all() เป็น CustomUser.objects.all()
    return render(request, 'user_management.html', {'users': users})

@staff_member_required
def delete_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)  # ✅ ใช้ CustomUser แทน User

    if user.is_staff:
        messages.error(request, "ไม่สามารถลบผู้ดูแลระบบได้")
    else:
        user.delete()
        messages.success(request, "ลบผู้ใช้งานเรียบร้อยแล้ว")

    return redirect('user_management')


from .models import Schedule  # เปลี่ยนจาก Reservation เป็น Schedule

@login_required
def user_reservations(request):
    reservations = Schedule.objects.filter(booked_by=request.user)
    return render(request, 'user_reservations.html', {'reservations': reservations})

