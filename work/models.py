from django.db import models
from django.contrib.auth.models import User


class WorkLog(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("INVOICED", "Invoiced"),
        ("PAID", "Paid"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="work_logs")
    company_client = models.ForeignKey(
        "clients.Client", on_delete=models.CASCADE, related_name="work_logs"
    )
    hours_worked = models.DecimalField(max_digits=5, decimal_places=2)
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    work_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    invoice_date = models.DateField(blank=True, null=True)
    invoice_number = models.CharField(max_length=50, blank=True, null=True)
    payment_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company_client.company_name} - {self.hours_worked}h @ £{self.hourly_rate}/h"

    class Meta:
        ordering = ["-work_date", "-created_at"]
        verbose_name = "Work Log"
        verbose_name_plural = "Work Logs"

    def save(self, *args, **kwargs):
        # Automatically set hourly rate from client if not set
        if not self.hourly_rate and self.company_client:
            self.hourly_rate = self.company_client.hourly_rate

        # Calculate total amount if not set
        if not self.total_amount:
            self.total_amount = self.hours_worked * self.hourly_rate

        super().save(*args, **kwargs)
