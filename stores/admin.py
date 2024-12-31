from django.contrib import admin
from .models import StoreProfile

@admin.register(StoreProfile)
class StoreProfileAdmin(admin.ModelAdmin):
    """Admin configuration for the StoreProfile model."""
    list_display = ('uuid', 'user', 'address', 'instagram_link')
    search_fields = ('user__email', 'address', 'instagram_link')
    list_filter = ('address',)
    readonly_fields = ('uuid',)

    fieldsets = (
        (None, {
            'fields': ('uuid', 'user', 'logo', 'address', 'instagram_link')
        }),
    )