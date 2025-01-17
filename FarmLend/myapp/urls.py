from django.urls import path
from . import views
from .views import profile_view

urlpatterns = [
    path('', views.welcome_view, name='welcome'),  # หน้าแรก
    path('login/', views.login_view, name='login'),  # หน้าล็อกอิน
    path('register/', views.register_view, name='register'),  # หน้าสมัคร
    path('logout/', views.logout_view, name='logout'),  # ล็อกเอาท์

    path('cars/types/', views.car_type_list_view, name='car_type_list'),  # แสดงประเภทของรถ
    path('cars/type/<int:type_id>/', views.car_list_by_type_view, name='car_list_by_type'),  # แสดงรถในแต่ละประเภท
    path('cars/<int:car_id>/', views.car_detail_view, name='car_detail'),  # แสดงรายละเอียดของรถ

    path('edicar/<int:id>/<int:type_id>/', views.edicar, name='edicar'),  # แก้ไขข้อมูลรถ
    path('delcar/<int:car_id>/<int:type_id>/', views.delcar, name='delcar'),  # ลบรถ

    path('confirm_selection/<str:time>/', views.confirm_selection, name='confirm_selection'),  # ยืนยันการเลือกเวลา
    path('car/schedule/<int:car_id>/', views.car_schedule, name='car_schedule'),  # ตารางงานของรถ

    path('book_time/<int:car_id>/', views.book_time, name='book_time'),  # จองเวลารถ

    path('approval_list/', views.car_approval_list, name='car_approval_list'),  # แสดงรายการรถที่รออนุมัติ
    path('approve_car/<int:car_id>/', views.approve_car, name='approve_car'),  # อนุมัติรถ
    path('addcar/<int:type_id>/', views.add_car, name='addcar'),  # เพิ่มรถใหม่

    path('pending-cars/', views.pending_car_list, name='pending_car_list'),  # รถที่รอการอนุมัติ
    path('delete-car/<int:car_id>/', views.delete_car, name='delete_car'),  # ลบรถ

    path('profile/', views.profile_view, name='profile'),  # ดูโปรไฟล์
    path('edit-profile/', views.edit_profile_view, name='edit_profile'),  # แก้ไขโปรไฟล์

    path('delete_car/<int:car_id>/', views.delete_car, name='delete_car'), 

    path('cars/<int:car_id>/toggle_status/', views.toggle_car_status, name='toggle_car_status'),  # เส้นทางที่ใช้สำหรับเปลี่ยนสถานะของรถ                                                                                       
    path('cars/<int:car_id>/schedule/', views.car_schedule, name='car_schedule'),

]
