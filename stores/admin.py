from django.contrib import admin
from .models import StoreProfile, Price

@admin.register(StoreProfile)
class StoreProfileAdmin(admin.ModelAdmin):
    """Admin configuration for the StoreProfile model."""
    list_display = ('uuid', 'user', 'store_name', 'address', 'instagram_link', 'whatsapp_number', 'average_rating', 'twogis')
    search_fields = ('user__email', 'store_name', 'address', 'instagram_link', 'whatsapp_number')
    list_filter = ('address',)
    readonly_fields = ('uuid',)

    fieldsets = (
        (None, {
            'fields': ('uuid', 'user', 'store_name', 'logo', 'address', 'instagram_link', 'whatsapp_number', 'average_rating', 'twogis')
        }),
    )

@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'order', 'store', 'proposed_price', 'is_accepted', 'created_at', 'updated_at', 'expires_at')
    list_filter = ('is_accepted',)
    search_fields = ('order__uuid', 'store__user__email')
    readonly_fields = ('uuid',)
    ordering = ('-created_at',)
    

    fieldsets = (
        (None, {
            'fields': ('order', 'store', 'proposed_price', 'flower_img', 'comment', 'is_accepted')
        }),
    )

