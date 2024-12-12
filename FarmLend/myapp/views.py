from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Car, CarType
from django.shortcuts import render
from .models import Car, Schedule
from  .forms import CarForm 


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
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists')
            elif User.objects.filter(email=email).exists():
                messages.error(request, 'Email already exists')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
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

# ฟังก์ชันแสดงรถในแต่ละประเภท
def car_list_by_type_view(request, type_id):
    """
    แสดงรายการรถในแต่ละประเภท:
    - กรองตามประเภทรถที่เลือก
    """
    car_type = get_object_or_404(CarType, id=type_id)
    cars = Car.objects.filter(car_type=car_type)
    return render(request, 'car_list.html', {'cars': cars, 'car_type': car_type})

# ฟังก์ชันแสดงรายละเอียดของรถแต่ละคัน
def car_detail_view(request, car_id):
    """
    แสดงรายละเอียดของรถแต่ละคัน
    """
    car = get_object_or_404(Car, pk=car_id)
    return render(request, 'car_detail.html', {'car': car})

# ฟังก์ชันเพิ่มรถ
def addcar(request, type):
    """
    เพิ่มรถใหม่:
    - ใช้ฟอร์ม CarForm
    - เมื่อเพิ่มสำเร็จจะเปลี่ยนไปยังหน้า car_list_by_type
    """
    if request.method == 'POST':
        form = CarForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('car_list_by_type', type=type)
    else:
        form = CarForm()

    return render(request, 'addcar.html', {'form': form, 'type': type})

# ฟังก์ชันแก้ไขรถ
def edicar(request, id, type):
    """
    แก้ไขข้อมูลรถที่มีอยู่:
    - ใช้ฟอร์ม CarForm พร้อมกับ instance ของรถที่ต้องการแก้ไข
    """
    car = Car.objects.get(pk=id)
    if request.method == 'POST':
        form = CarForm(request.POST, request.FILES, instance=car)
        if form.is_valid():
            form.save()
            return redirect('car_list_by_type', type=type)
    else:
        form = CarForm(instance=car)

    return render(request, 'edicar.html', {'form': form})

# ฟังก์ชันลบรถ
def delcar(request, id, type):
    """
    ลบรถตาม ID:
    - เมื่อเสร็จจะเปลี่ยนไปยังหน้า car_list_by_type
    """
    Car.objects.get(pk=id).delete()
    return redirect('car_list_by_type', type=type)

# ฟังก์ชันแสดงตารางงานของรถ
def car_schedule(request, car_id):
    """
    แสดงตารางงานของรถ:
    - แสดงรายการตารางที่เกี่ยวข้องกับรถ
    """
    car = get_object_or_404(Car, id=car_id)
    schedules = Schedule.objects.filter(car=car)
    return render(request, 'car_schedule.html', {'car': car, 'schedules': schedules})

# ฟังก์ชันยืนยันการเลือกเวลา
def confirm_selection(request):
    """
    ยืนยันการเลือกวันที่และช่วงเวลา:
    - ตรวจสอบข้อมูลก่อนส่งไปยัง Template
    """
    selected_date = request.GET.get('date')
    selected_time = request.GET.get('time')
    if not selected_date or not selected_time:
        return render(request, 'error.html', {'message': 'กรุณาเลือกวันที่และช่วงเวลาให้ครบถ้วน'})

    context = {
        'date': selected_date,
        'time': 'ช่วงเช้า' if selected_time == 'morning' else 'ช่วงบ่าย',
    }
    return render(request, 'confirm_selection.html', context)
