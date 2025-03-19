# chatbot/views.py
from django.shortcuts import render
from django.http import JsonResponse
from .models import Message

def chatbot(request):
    return render(request, 'chatbot/chatbot.html')

def chat_logs(request):
    logs = Message.objects.all().order_by('timestamp')
    data = [{"sender": "user" if msg.sender else "bot", "message": msg.content, "timestamp": msg.timestamp} for msg in logs]
    return JsonResponse({"logs": data})

