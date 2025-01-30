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

    # ตรวจสอบว่าเจ้าของรถหรือแอดมินหรือไม่
    if request.user != car.owner and not request.user.is_staff:
        return HttpResponseForbidden("คุณไม่มีสิทธิ์ในการแก้ไขรถคันนี้")

    if request.method == 'POST':
        form = CarForm(request.POST, instance=car)
        if form.is_valid():
            form.save()
            # หลังจากบันทึกแล้วให้กลับไปที่หน้ารายละเอียดของรถที่แก้ไข
            return redirect('car_detail', car_id=car.id)  # เปลี่ยนไปหน้ารายละเอียดของรถที่แก้ไข
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

def book_time(request, car_id):
    # ดึงข้อมูลรถที่ต้องการจอง
    car = get_object_or_404(Car, pk=car_id)

    if request.method == 'POST':
        selected_date = request.POST.get('date')  # รับวันที่จากฟอร์ม
        selected_time = request.POST.get('time')  # รับช่วงเวลาจากฟอร์ม

        # ตรวจสอบว่าได้เลือกข้อมูลครบถ้วนหรือยัง
        if selected_date and selected_time:
            # ส่งข้อมูลไปยังหน้าแจ้งเตือน
            return redirect('confirm_selection', date=selected_date, time=selected_time, car_id=car.id)
        else:
            # ถ้าข้อมูลไม่ครบถ้วน จะส่ง error message ไปยังหน้าจอง
            return render(request, 'error.html', {'message': 'กรุณาเลือกวันที่และช่วงเวลาให้ครบถ้วน'})

    # ถ้าไม่ใช่ POST, ให้แสดงฟอร์มสำหรับเลือกเวลาและวันที่
    return render(request, 'book_time.html', {'car': car})

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


def delete_car(request, car_id):
    # ตรวจสอบว่าเป็น admin หรือไม่
    if not request.user.is_staff:
        return redirect('car_type_list')  # ไม่ให้ลบหากไม่ใช่ admin

    car = get_object_or_404(Car, id=car_id)  # ค้นหารถที่ต้องการลบ
    car.delete()  # ลบข้อมูลรถ
    return JsonResponse({'success': True})  # ส่งการตอบกลับว่าให้ลบรถสำเร็จ


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
def confirm_reservation(request, reservation_id):
    # ตรวจสอบว่ามีการจองนี้ในระบบหรือไม่
    schedule = get_object_or_404(Schedule, id=reservation_id)

    if request.method == 'POST':
        action = request.POST.get('action')  # ค่าจากปุ่มยืนยันหรือปฏิเสธ
        
        if action == 'approve':
            # ถ้าเลือกยืนยัน
            schedule.is_booked = True  # อัพเดตสถานะการจองให้เป็นยืนยัน
            schedule.save()

            # สร้างการแจ้งเตือนให้ผู้จองทราบว่าเจ้าของรถยืนยันการจองแล้ว
            Notification.objects.create(
                user=schedule.car.owner,  # เจ้าของรถ
                message=f"เจ้าของรถ {schedule.car.name} ได้รับการยืนยันการจองแล้ว สำหรับวันที่ {schedule.date} เวลา {schedule.time}",
                schedule=schedule,
                is_confirmed=True,
                is_approved=True  # ตั้งค่าการยืนยันการจอง
            )
        elif action == 'reject':
            # ถ้าเลือกปฏิเสธ
            schedule.is_booked = False  # เปลี่ยนสถานะเป็นไม่ยืนยัน
            schedule.save()

            # สร้างการแจ้งเตือนให้ผู้จองทราบว่าเจ้าของรถปฏิเสธการจอง
            Notification.objects.create(
                user=schedule.car.owner,  # เจ้าของรถ
                message=f"เจ้าของรถ {schedule.car.name} ได้ปฏิเสธการจองของคุณ สำหรับวันที่ {schedule.date} เวลา {schedule.time}",
                schedule=schedule,
                is_confirmed=True,
                is_approved=False  # ตั้งค่าการปฏิเสธการจอง
            )

        return redirect('notification_list')  # รีไดเรกต์ไปที่หน้าการแจ้งเตือนของผู้จอง


# ฟังก์ชันการสร้างการจอง
def confirm_booking(request):
    if request.method == 'POST':
        selected_date = request.POST.get('date')
        selected_time = request.POST.get('time')
        car_id = request.POST.get('car_id')

        # ตรวจสอบข้อมูล
        if not selected_date or not selected_time or not car_id:
            return render(request, 'error.html', {'message': 'ข้อมูลไม่ครบถ้วน'})
        
        # ดึงข้อมูลรถ
        car = get_object_or_404(Car, id=car_id)
        
        # สร้างการจองในสถานะ "รอการยืนยัน"
        schedule = Schedule.objects.create(
            car=car,
            date=selected_date,
            time=selected_time,
            is_booked=False  # รอการยืนยันจากเจ้าของรถ
        )

        # ตรวจสอบว่า schedule ถูกสร้างหรือไม่
        if schedule:
            # สร้างการแจ้งเตือนให้เจ้าของรถ
            Notification.objects.create(
                user=car.owner,
                message=f"คุณมีการจองรถ {car.name} จาก {request.user.username} สำหรับวันที่ {selected_date} ช่วงเวลา {selected_time}. โปรดตรวจสอบและอนุมัติ",
                schedule=schedule  # ผูกการแจ้งเตือนกับการจอง
            )

            messages.success(request, "การจองถูกบันทึกและแจ้งเตือนไปยังเจ้าของรถแล้ว.")
            return redirect('notification_list')  # เปลี่ยนไปหน้าแสดงรายการแจ้งเตือน
        else:
            messages.error(request, "เกิดข้อผิดพลาดในการสร้างการจอง")
    
    return render(request, 'book_time.html', {'car': car})


@login_required
def create_booking(request, car_id):
    car = get_object_or_404(Car, id=car_id)

    if request.method == 'POST':
        selected_date = request.POST.get('date')
        selected_time = request.POST.get('time')

        if selected_date and selected_time:
            # สร้างการจองในฐานข้อมูล
            schedule = Schedule.objects.create(
                car=car,
                date=selected_date,
                time=selected_time,
                is_booked=False  # การจองยังไม่ได้รับการยืนยัน
            )

            # สร้างการแจ้งเตือนให้เจ้าของรถ
            Notification.objects.create(
                user=car.owner,
                message=f"คุณมีการจองรถ {car.name} จาก {request.user.username} สำหรับวันที่ {selected_date} ช่วงเวลา {selected_time}. โปรดตรวจสอบและอนุมัติ",
                schedule=schedule  # ผูกการแจ้งเตือนกับการจอง
            )

            messages.success(request, "การจองถูกบันทึกและแจ้งเตือนไปยังเจ้าของรถแล้ว.")
            return redirect('notification_list')  # เปลี่ยนไปหน้าแสดงรายการแจ้งเตือน

        else:
            messages.error(request, "กรุณาเลือกวันที่และช่วงเวลาให้ครบถ้วน.")
    
    return render(request, 'book_time.html', {'car': car})

def notification_list(request):
    # ตรวจสอบว่า user ได้รับการแจ้งเตือนหรือไม่
    notifications = Notification.objects.filter(user=request.user).order_by('-timestamp')  # เรียงตามเวลาล่าสุดก่อน

    # ส่งข้อมูลไปที่ template
    return render(request, 'notification_list.html', {'notifications': notifications})


def parse_date(date_str):
    try:
        # แปลงวันที่จากรูปแบบที่ไม่ตรงกับ Django ไปเป็น YYYY-MM-DD
        return datetime.strptime(date_str, '%d-%m-%Y').strftime('%Y-%m-%d')
    except ValueError:
        return None


from .models import Car, Review
from .forms import ReviewForm

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

