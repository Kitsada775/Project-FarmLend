from django.urls import path
from . import views

urlpatterns = [

    # หน้าแรกและระบบสมาชิก
    path('', views.welcome_view, name='welcome'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # จัดการประเภทและรายการรถ
    path('cars/types/', views.car_type_list_view, name='car_type_list'),
    path('cars/type/<int:type_id>/', views.car_list_by_type, name='car_list_by_type'),
    path('cars/<int:car_id>/', views.car_detail_view, name='car_detail'),
    path('car_list/', views.car_list_view, name='car_list'),

    # จัดการรถ (เพิ่ม, แก้ไข, ลบ)
    path('addcar/<int:type_id>/', views.add_car, name='addcar'),
    path('editcar/<int:id>/<int:type_id>/', views.edicar, name='edit_car'),
    path('edit_car/<int:id>/<int:type_id>/', views.edicar, name='edicar'),
    path('delete_car/<int:car_id>/<int:type_id>/', views.delete_car, name='delcar'),
    path('cars/<int:car_id>/toggle_status/', views.toggle_car_status, name='toggle_car_status'),
    path('my-cars/', views.my_cars, name='my_cars'),

    # อนุมัติและการจัดการรถ
    path('pending-cars/', views.car_pending_list, name='pending_car_list'),
    path('approval_list/', views.car_pending_list, name='car_approval_list'),
    path('approve_car/<int:car_id>/', views.approve_car, name='approve_car'),

    # ระบบการจองรถ
    path('car/schedule/<int:car_id>/', views.car_schedule, name='car_schedule'),
    path('confirm_selection/', views.confirm_selection, name='confirm_selection'),
    path('cars/<int:car_id>/book_time/', views.book_time, name='book_time'),
    path('cars/<int:car_id>/create_booking/', views.create_booking, name='create_booking'),
    path('create_booking/<int:car_id>/', views.create_booking, name='create_booking'),
    
    # การยืนยันและยกเลิกการจอง
    path('confirm_reservation/<int:schedule_id>/', views.confirm_reservation, name='confirm_reservation'),
    path('cancel_reservation/<int:reservation_id>/', views.cancel_reservation, name='cancel_reservation'),
    path('my_reservations/', views.user_reservations, name='user_reservations'),

    # การแจ้งเตือน
    path('notification_list/', views.notification_list, name='notification_list'),

    # จัดการผู้ใช้
    path('profile/', views.profile_view, name='profile'),
    path('edit-profile/', views.edit_profile_view, name='edit_profile'),
    path('users/', views.user_management, name='user_management'),
    path('users/delete/<int:user_id>/', views.delete_user, name='delete_user'),

    # ระบบรีวิวรถ
    path('car/<int:car_id>/reviews/', views.car_review_view, name='car_review'),





    path('delete_car/<int:car_id>/', views.delete_car, name='delete_car'),
    


]
