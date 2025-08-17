from django.db import models
from django.contrib.auth.models import User

class Income(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='incomes')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=200)
    payer = models.CharField(max_length=100, blank=True, null=True)
    date = models.DateField()
    category = models.ForeignKey('categories.Category', on_delete=models.PROTECT, related_name='income')
    is_taxable = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.description} - £{self.amount} ({self.date})"
    
    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name = 'Income'
        verbose_name_plural = 'Incomes'
