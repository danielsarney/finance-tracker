from django.db import models
from finance_tracker.mixins import BaseFinancialModel

class Subscription(BaseFinancialModel):
    BILLING_CYCLE_CHOICES = [
        ('DAILY', 'Daily'),
        ('WEEKLY', 'Weekly'),
        ('MONTHLY', 'Monthly'),
        ('QUARTERLY', 'Quarterly'),
        ('YEARLY', 'Yearly'),
    ]
    
    name = models.CharField(max_length=200)
    billing_cycle = models.CharField(max_length=20, choices=BILLING_CYCLE_CHOICES, default='MONTHLY')
    next_billing_date = models.DateField()
    is_auto_renewed = models.BooleanField(default=False, help_text="Whether this subscription automatically renews")
    is_business_expense = models.BooleanField(default=False, help_text="Whether this subscription is a business expense")
    
    class Meta:
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'
        ordering = ['next_billing_date', 'name']
    
    def save(self, *args, **kwargs):
        if not self.next_billing_date:
            self.next_billing_date = self.date
        super().save(*args, **kwargs)
