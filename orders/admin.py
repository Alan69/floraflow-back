from django.contrib import admin
from .models import Order, Flower, Color

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin configuration for the Order model."""
    list_display = ('uuid', 'client', 'store', 'flower', 'color', 'flower_height', 'quantity', 'price', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'flower', 'color', 'created_at', 'updated_at')
    search_fields = ('client__email', 'store__email', 'uuid', 'flower__text', 'color__text')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (None, {
            'fields': ('client', 'store', 'flower', 'color', 'flower_height', 'quantity', 'city', 'recipients_address', 'recipients_phone', 'flower_data', 'price', 'status', 'created_at', 'updated_at', 'rating')
        }),
    )

admin.site.register(Flower)
admin.site.register(Color)