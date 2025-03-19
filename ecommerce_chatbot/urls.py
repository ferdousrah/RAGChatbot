# ecommerce_chatbot/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('chat/', include('chatbot.urls')),  # This includes the chatbot's URLs
]