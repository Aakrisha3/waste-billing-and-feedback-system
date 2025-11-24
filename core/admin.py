from django.contrib import admin
from .models import Customer, WasteItem, Bill, Feedback

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'customer_type', 'monthly_rate', 'email')
    search_fields = ('name', 'email')
    list_filter = ('customer_type',)

@admin.register(WasteItem)
class WasteItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'unit_price')
    search_fields = ('name',)

@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'total_amount', 'status', 'date_created', 'month', 'year', 'paid')
    search_fields = ('customer__name',)
    list_filter = ('status', 'month', 'year', 'paid')
    readonly_fields = ('total_amount',)

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'comment', 'created_at')
    search_fields = ('customer__name', 'comment')
    list_filter = ('created_at',)
