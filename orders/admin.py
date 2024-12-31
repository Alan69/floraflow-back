from django.contrib import admin
from .models import Order

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin configuration for the Order model."""
    list_display = ('uuid', 'client', 'store', 'price', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at', 'updated_at')
    search_fields = ('client__email', 'store__email', 'uuid')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (None, {
            'fields': ('uuid', 'client', 'store', 'flower_data', 'price', 'status', 'created_at', 'updated_at')
        }),
    )