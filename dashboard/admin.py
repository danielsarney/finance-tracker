from django.contrib import admin
from .models import FinancialSummary

@admin.register(FinancialSummary)
class FinancialSummaryAdmin(admin.ModelAdmin):
    list_display = ['user', 'month', 'year', 'total_income', 'total_expenses', 'net_income', 'total_subscriptions']
    list_filter = ['month', 'year', 'user']
    search_fields = ['user__username']
    list_per_page = 25
