# chat/models.py
from django.db import models
from django.conf import settings
from myapp.models import Car   # ใช้การ import โมเดลจากแอป myapp โดยตรง

class ChatRoom(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='chat_rooms')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)  # Add this to mark if chat is still active
    last_message_at = models.DateTimeField(auto_now=True)  # Add this to track latest activity

    class Meta:
        ordering = ['-last_message_at']  # Sort by most recent activity

    def __str__(self):
        return f"Chat Room for {self.car.name} with {', '.join([user.username for user in self.participants.all()])}"

    def get_other_participant(self, user):
        """Helper method to get the other participant"""
        return self.participants.exclude(id=user.id).first()

class Message(models.Model):
    chat_room = models.ForeignKey(ChatRoom, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)  # Add this to track read status

    class Meta:
        ordering = ['timestamp']  # Sort messages chronologically

    def __str__(self):
        return f"{self.sender.username}: {self.content}"

    def mark_as_read(self):
        """Helper method to mark message as read"""
        self.is_read = True
        self.save()


