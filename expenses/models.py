from django.db import models
from finance_tracker.mixins import BaseFinancialModel


class Expense(BaseFinancialModel):
    description = models.CharField(max_length=200)
    payee = models.CharField(max_length=100, blank=True, null=True)
    is_tax_deductible = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Expense"
        verbose_name_plural = "Expenses"
