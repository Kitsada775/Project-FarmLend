from django.shortcuts import render, redirect
from django.shortcuts import render, get_object_or_404
from .models import ChatRoom, Message
from .forms import MessageForm
from .models import ChatRoom, Car
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.core.exceptions import PermissionDenied


def chatPage(request):
    # ดึงห้องแชททั้งหมด
    chat_rooms = ChatRoom.objects.all()
    return render(request, "chat/chatPage.html", {"chat_rooms": chat_rooms})


@login_required
def create_chat_room(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    
    # Check if chat room already exists
    chat_room = ChatRoom.objects.filter(
        car=car,
        participants=request.user
    ).first()
    
    if not chat_room:
        # Create new chat room and add both user and car owner
        chat_room = ChatRoom.objects.create(car=car)
        chat_room.participants.add(request.user, car.owner)
    
    return redirect('chat_room', room_id=chat_room.id)

# views.py
@login_required
def chat_room(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)
    
    # Check if user is authorized (either owner or participant)
    if request.user != room.car.owner and request.user not in room.participants.all():
        return HttpResponseForbidden("Not authorized")
    
    # Get the other participant
    other_participant = room.get_other_participant(request.user)
    
    context = {
        'room': room,
        'messages': room.messages.all().order_by('timestamp'),
        'other_participant': other_participant,
        'is_owner': request.user == room.car.owner
    }
    
    return render(request, 'chat_room.html', context)


@login_required
def my_chats(request):
    # ดึงห้องแชททั้งหมดที่ผู้ใช้เป็น participant (ทั้งเจ้าของรถและผู้สนใจ)
    chats = ChatRoom.objects.filter(participants=request.user).distinct()

    return render(request, 'owner_chats.html', {
        'chats': chats
    })
