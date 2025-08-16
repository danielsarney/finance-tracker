from django.contrib import admin
from .models import Subscription

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['name', 'amount', 'billing_cycle', 'status', 'next_billing_date', 'user']
    list_filter = ['billing_cycle', 'status', 'user']
    search_fields = ['name', 'description', 'notes']
    date_hierarchy = 'start_date'
    list_per_page = 25
