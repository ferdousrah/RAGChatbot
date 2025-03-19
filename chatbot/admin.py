# chatbot/admin.py
from django.contrib import admin
from .models import Product, KnowledgeBase, Message

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock_quantity')
    search_fields = ('name', 'category')
    list_filter = ('category',)
    ordering = ('name',)
    readonly_fields = ('id',)
    fields = (
        'id', 
        'name', 
        'description', 
        'price', 
        'category', 
        'stock_quantity', 
        'specifications', 
        'image'
    )

@admin.register(KnowledgeBase)
class KnowledgeBaseAdmin(admin.ModelAdmin):
    list_display = ('question',)
    search_fields = ('question', 'answer')
    ordering = ('question',)
    readonly_fields = ('id',)
    fields = ('id', 'question', 'answer')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'content', 'timestamp')  # Fields to display in the list view
    search_fields = ('sender', 'content')  # Enable search for sender and content
    list_filter = ('timestamp',)  # Filter messages by timestamp
    ordering = ('-timestamp',)  # Order messages by timestamp (latest first)
    readonly_fields = ('timestamp',)  # Make the timestamp field read-only
