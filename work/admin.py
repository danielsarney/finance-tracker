from django.contrib import admin
from .models import WorkLog

@admin.register(WorkLog)
class WorkLogAdmin(admin.ModelAdmin):
    list_display = ['company_client', 'hours_worked', 'hourly_rate', 'total_amount', 'work_date', 'status', 'user']
    list_filter = ['status', 'work_date', 'user']
    search_fields = ['company_client', 'description', 'invoice_number', 'notes']
    date_hierarchy = 'work_date'
    list_per_page = 25
