from django.urls import path
from . import views

urlpatterns = [
    path('', views.welcome_view, name='welcome'),  # หน้าแรก
    path('login/', views.login_view, name='login'),  # หน้าล็อกอิน
    path('register/', views.register_view, name='register'),  # หน้าสมัคร
    path('logout/', views.logout_view, name='logout'),  # ล็อกเอาท์

    path('cars/types/', views.car_type_list_view, name='car_type_list'),  # แสดงประเภทของรถ
    path('cars/type/<int:type_id>/', views.car_list_by_type_view, name='car_list_by_type'),  # แสดงรถในแต่ละประเภท
    path('cars/<int:car_id>/', views.car_detail_view, name='car_detail'),  # แสดงรายละเอียดของรถ

    path('types/', views.car_type_list_view, name='car_type_list'),
    path('types/<int:type_id>/', views.car_list_by_type_view, name='car_list_by_type'),

    path('addcar/<str:type>/',views.addcar,name='addcar'),
    path('edicar/<int:id>/<str:type>/',views.edicar,name='edicar'),
    path('delcar/<int:id>/<str:type>/',views.delcar,name='delcar'),

]
