from django.db import models
from finance_tracker.mixins import BaseFinancialModel

class Income(BaseFinancialModel):
    payer = models.CharField(max_length=100, blank=True, null=True)
    is_taxable = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Income'
        verbose_name_plural = 'Incomes'
