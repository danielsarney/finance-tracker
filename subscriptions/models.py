from django.db import models
from django.contrib.auth.models import User

class Subscription(models.Model):
    BILLING_CYCLE_CHOICES = [
        ('DAILY', 'Daily'),
        ('WEEKLY', 'Weekly'),
        ('MONTHLY', 'Monthly'),
        ('QUARTERLY', 'Quarterly'),
        ('YEARLY', 'Yearly'),
    ]
    
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    billing_cycle = models.CharField(max_length=20, choices=BILLING_CYCLE_CHOICES, default='MONTHLY')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    start_date = models.DateField()
    next_billing_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    auto_renew = models.BooleanField(default=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - £{self.amount}/{self.billing_cycle.lower()}"
    
    class Meta:
        ordering = ['next_billing_date', 'name']
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'
    
    def save(self, *args, **kwargs):
        if not self.next_billing_date:
            self.next_billing_date = self.start_date
        super().save(*args, **kwargs)
