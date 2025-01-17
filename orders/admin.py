from django.contrib import admin
from .models import Order, Flower, Color

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin configuration for the Order model."""
    list_display = ('uuid', 'client', 'store', 'price', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at', 'updated_at')
    search_fields = ('client__email', 'store__email', 'uuid')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (None, {
            'fields': ('client', 'store', 'flower_data', 'price', 'status', 'created_at', 'updated_at')
        }),
    )

admin.site.register(Flower)
admin.site.register(Color)