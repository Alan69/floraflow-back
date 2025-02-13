from django.contrib import admin
from .models import StoreProfile, Price

@admin.register(StoreProfile)
class StoreProfileAdmin(admin.ModelAdmin):
    """Admin configuration for the StoreProfile model."""
    list_display = ('uuid', 'user', 'address', 'instagram_link', 'whatsapp_number', 'average_rating')
    search_fields = ('user__email', 'address', 'instagram_link', 'whatsapp_number')
    list_filter = ('address',)
    readonly_fields = ('uuid',)

    fieldsets = (
        (None, {
            'fields': ('uuid', 'user', 'logo', 'address', 'instagram_link', 'whatsapp_number', 'average_rating')
        }),
    )

admin.site.register(Price)