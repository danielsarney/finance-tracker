from django.db import models
from django.contrib.auth.models import User


class FinancialSummary(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="financial_summaries"
    )
    month = models.IntegerField()  # 1-12
    year = models.IntegerField()
    total_income = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_expenses = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    net_income = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_subscriptions = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00
    )
    total_work_income = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.month}/{self.year}"

    class Meta:
        unique_together = ["user", "month", "year"]
        ordering = ["-year", "-month"]
        verbose_name = "Financial Summary"
        verbose_name_plural = "Financial Summaries"

    def save(self, *args, **kwargs):
        self.net_income = self.total_income - self.total_expenses
        super().save(*args, **kwargs)
