from django.urls import path, include
from chat import views as chat_views
from django.contrib.auth.views import LoginView, LogoutView
from . import views

appname = "chat"

urlpatterns = [
    path("chat/", chat_views.chatPage, name="chat-page"),

    path('create-chat/<int:car_id>/', views.create_chat_room, name='create_chat_room'),
    path('chat/<int:room_id>/', views.chat_room, name='chat_room'),
    path('my-chats/', views.owner_chats, name='owner_chats'),

]
