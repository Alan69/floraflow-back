from django.contrib import admin
from .models import Tariff, TariffHistory

@admin.register(TariffHistory)
class TariffHistoryAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'tariff_name', 'tariff_price', 'created_at')
    list_filter = ('created_at', 'tariff', 'user')
    search_fields = ('user__email', 'tariff__name')
    date_hierarchy = 'created_at'
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User Email'
    
    def tariff_name(self, obj):
        return obj.tariff.name
    tariff_name.short_description = 'Tariff Name'
    
    def tariff_price(self, obj):
        return obj.tariff.price
    tariff_price.short_description = 'Price'

# Register your models here.
admin.site.register(Tariff)