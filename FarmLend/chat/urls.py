from django.urls import path, include
from chat import views as chat_views
from django.contrib.auth.views import LoginView, LogoutView

appname = "chat"

urlpatterns = [
    path("chat/", chat_views.chatPage, name="chat-page"),


]
