from django.contrib import admin
from .models import Product, Enquiry

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_available', 'created_at')
    list_filter = ('category', 'is_available', 'created_at')
    search_fields = ('name', 'category', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('price', 'is_available')
    ordering = ('-created_at',)
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'category', 'price', 'is_available')
        }),
        ('Media & Details', {
            'fields': ('image', 'description')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'product', 'created_at')
    list_filter = ('created_at', 'product')
    search_fields = ('name', 'phone', 'message')
    readonly_fields = ('name', 'phone', 'product', 'message', 'created_at')
    ordering = ('-created_at',)
