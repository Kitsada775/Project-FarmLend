from django.urls import path
from . import views
from .views import notification_list
from .views import user_management, delete_user
from .views import delete_car
from .views import user_reservations
from .views import cancel_reservation

urlpatterns = [

    path('export-code/<str:app_name>/', views.app_to_pdf, name='export_code'),

    # หน้าแรก
    path('', views.welcome_view, name='welcome'), 

    # หน้าเข้าสู่ระบบ
    path('login/', views.login_view, name='login'), 

    # หน้าไปยังหน้าลงทะเบียน
    path('register/', views.register_view, name='register'), 

    # ล็อกเอาท์
    path('logout/', views.logout_view, name='logout'), 

    # แสดงประเภทของรถ
    path('cars/types/', views.car_type_list_view, name='car_type_list'), 

    # แสดงรถในแต่ละประเภท
    path('cars/type/<int:type_id>/', views.car_list_by_type_view, name='car_list_by_type'), 

    # แสดงรายละเอียดของรถ
    path('cars/<int:car_id>/', views.car_detail_view, name='car_detail'), 

    # แก้ไขข้อมูลรถ
    path('edicar/<int:id>/<int:type_id>/', views.edicar, name='edicar'), 

    # ลบรถ
    path('delcar/<int:car_id>/<int:type_id>/', views.delcar, name='delcar'), 
    path('delete_car/<int:car_id>/', delete_car, name='delete_car'),

    # ตารางงานของรถ
    path('car/schedule/<int:car_id>/', views.car_schedule, name='car_schedule'), 


    # แสดงรายการรถที่รออนุมัติ
    path('approval_list/', views.car_approval_list, name='car_approval_list'), 

    # อนุมัติรถ
    path('approve_car/<int:car_id>/', views.approve_car, name='approve_car'), 

    # เพิ่มรถใหม่
    path('addcar/<int:type_id>/', views.add_car, name='addcar'), 

    # รถที่รอการอนุมัติ
    path('pending-cars/', views.pending_car_list, name='pending_car_list'), 

    # ลบรถ
    path('delete-car/<int:car_id>/', views.delete_car, name='delete_car'), 

    # ดูโปรไฟล์
    path('profile/', views.profile_view, name='profile'), 

    # แก้ไขโปรไฟล์
    path('edit-profile/', views.edit_profile_view, name='edit_profile'), 

    # เปลี่ยนสถานะของรถ
    path('cars/<int:car_id>/toggle_status/', views.toggle_car_status, name='toggle_car_status'), 

    # เส้นทางสำหรับแสดงข้อมูลรถของผู้ใช้
    path('my-cars/', views.my_cars, name='my_cars'), 

    # ยืนยันการเลือกเวลา
    path('confirm_selection/', views.confirm_selection, name='confirm_selection'), 

    # แก้ไขรถ
    path('edit_car/<int:car_id>/', views.edicar, name='edit_car'),

    # สร้างการจอง
    path('create_booking/<int:car_id>/', views.create_booking, name='create_booking'),

    # ยืนยันการจอง
    path('confirm_reservation/<int:reservation_id>/', views.confirm_reservation, name='confirm_reservation'),

    # แสดงรายการการแจ้งเตือน
    path('notification_list/', views.notification_list, name='notification_list'), 

    # เส้นทางแสดงรายการรถทั้งหมด
    path('car_list/', views.car_list_view, name='car_list'),  # แสดงรายการรถทั้งหมด

    # เส้นทางแสดงรถในแต่ละประเภท
    path('cars/', views.car_list_view, name='car_list'),  # ควรใช้ URL สำหรับ car_list

    path('cars/<int:car_id>/reviews/', views.car_review_view, name='car_review'),  # เพิ่มเส้นทางนี้

    path('notification_list/', notification_list, name='notification_list'),
    
    path('users/', user_management, name='user_management'),
    path('users/delete/<int:user_id>/', delete_user, name='delete_user'),


    path('cancel_reservation/<int:reservation_id>/', views.cancel_reservation, name='cancel_reservation'),# เส้นทางสำหรับยกเลิกการจอง
    path('my_reservations/', views.user_reservations, name='user_reservations'),# เส้นทางสำหรับดูการจองของผู้ใช้




]
