from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Car, CarType

# ฟังก์ชันสำหรับหน้าแรก
def welcome_view(request):
    return render(request, 'welcome.html')

# ฟังก์ชันสำหรับหน้าล็อกอิน
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('car_type_list')  # ไปยังหน้าแสดงประเภทของรถ
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'login.html')

# ฟังก์ชันสำหรับหน้าสมัคร
def register_view(request):
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
    logout(request)
    return redirect('login')

# ฟังก์ชันแสดงรายการประเภทของรถ
def car_type_list_view(request):
    car_types = CarType.objects.all()  # ดึงข้อมูลประเภทของรถทั้งหมด
    return render(request, 'car_type_list.html', {'car_types': car_types})

# ฟังก์ชันแสดงรถในแต่ละประเภท
def car_list_by_type_view(request, type_id):
    car_type = get_object_or_404(CarType, id=type_id)  # ดึงประเภทของรถที่ต้องการ
    cars = Car.objects.filter(car_type=car_type)  # ดึงรถตามประเภทที่เลือก
    return render(request, 'car_list.html', {'cars': cars, 'car_type': car_type})

# ฟังก์ชันแสดงรายละเอียดของรถแต่ละคัน
def car_detail_view(request, car_id):
    car = get_object_or_404(Car, pk=car_id)
    return render(request, 'car_detail.html', {'car': car})

def car_type_list_view(request):
    car_types = CarType.objects.all()
    return render(request, 'car_types.html', {'car_types': car_types})

from  .forms import CarForm 
def addcar(request,type): #เพิ่มรถจากข้างนอก
    if request.method == 'POST' :
        form = CarForm(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            return redirect(f'/types/{type}/')
        else:
            form = CarForm()
    else:
        form = CarForm()
    
    return render(request, 'addcar.html',{'form':form})

def edicar(request,id,type): #แก้ไขข้อมูลรถ
    car = Car.objects.get(pk=id)
    if request.method == 'POST' :
        form = CarForm(request.POST,request.FILES,instance=car)
        if form.is_valid():
            form.save()
            return redirect(f'/types/{type}/')
        else:
            form = CarForm(instance=car)
    else:
        form = CarForm(instance=car)
    
    return render(request, 'edicar.html',{'form':form})

def delcar(request,id,type): #ลบ
    car = Car.objects.get(pk=id).delete()
    return redirect(f'/types/{type}/')