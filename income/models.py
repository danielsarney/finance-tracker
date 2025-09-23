from django.db import models
from finance_tracker.mixins import BaseFinancialModel


class Income(BaseFinancialModel):
    description = models.CharField(max_length=200)
    payer = models.CharField(max_length=100, blank=True, null=True)
    is_taxable = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Income"
        verbose_name_plural = "Incomes"
