# chatbot/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.chatbot, name='chatbot'),  # HTTP URL for the chatbot page
    path('logs/', views.chat_logs, name='chat_logs'),
]
