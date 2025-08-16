from django.contrib import admin
from .models import Expense

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['description', 'amount', 'date', 'user', 'is_taxable']
    list_filter = ['is_taxable', 'date', 'user']
    search_fields = ['description', 'payee', 'notes']
    date_hierarchy = 'date'
    list_per_page = 25
