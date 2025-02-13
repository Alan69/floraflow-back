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

admin.site.register(Price)