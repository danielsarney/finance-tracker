from django.contrib import admin
from .models import Income

@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ['description', 'amount', 'date', 'user', 'is_taxable']
    list_filter = ['is_taxable', 'date', 'user']
    search_fields = ['description', 'payer', 'notes']
    date_hierarchy = 'date'
    list_per_page = 25
