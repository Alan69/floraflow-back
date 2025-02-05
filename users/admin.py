from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone', 'city', 'user_type', 'profile_picture', 'current_order', 'tariff', 'tariff_days', 'invoice_id')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'phone', 'user_type', 'city', 'is_staff', 'is_active')}
        ),
    )
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'user_type', 'last_login', 'date_joined')
    search_fields = ('email', 'first_name', 'last_name', 'phone')
    ordering = ('email',)
