from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import math


class ClockSession(models.Model):
    """Model to track clock in/out sessions"""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="clock_sessions"
    )
    client = models.ForeignKey(
        "clients.Client", on_delete=models.CASCADE, related_name="clock_sessions"
    )
    clock_in_time = models.DateTimeField()
    clock_out_time = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        status = "Active" if self.is_active else "Completed"
        return f"{self.client.company_name} - {self.clock_in_time.strftime('%Y-%m-%d %H:%M')} ({status})"

    class Meta:
        ordering = ["-clock_in_time"]
        verbose_name = "Clock Session"
        verbose_name_plural = "Clock Sessions"

    def clock_out(self):
        """Clock out and calculate hours worked"""
        if self.is_active:
            self.clock_out_time = timezone.now()
            self.is_active = False
            self.save()
            return self.calculate_hours()
        return 0

    def calculate_hours(self):
        """Calculate hours worked, rounding up to the nearest hour"""
        if not self.clock_out_time:
            return 0

        duration = self.clock_out_time - self.clock_in_time
        hours = duration.total_seconds() / 3600  # Convert to hours

        # Round up to the nearest hour (minimum 1 hour)
        rounded_hours = max(1, math.ceil(hours))
        return rounded_hours

    def get_duration_display(self):
        """Get human-readable duration"""
        if not self.clock_out_time:
            return "In Progress"

        duration = self.clock_out_time - self.clock_in_time
        hours = int(duration.total_seconds() // 3600)
        minutes = int((duration.total_seconds() % 3600) // 60)

        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"


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

    @classmethod
    def create_or_update_from_clock_session(cls, user, client, work_date, hours_to_add):
        """Create a new work log or update existing one for the same client and date"""
        try:
            # Try to find existing work log for the same client and date
            work_log = cls.objects.get(
                user=user, company_client=client, work_date=work_date
            )
            # Update existing work log
            work_log.hours_worked += hours_to_add
            work_log.total_amount = work_log.hours_worked * work_log.hourly_rate
            work_log.save()
            return work_log, False  # False indicates updated existing
        except cls.DoesNotExist:
            # Create new work log
            work_log = cls.objects.create(
                user=user,
                company_client=client,
                work_date=work_date,
                hours_worked=hours_to_add,
                hourly_rate=client.hourly_rate,
                total_amount=hours_to_add * client.hourly_rate,
            )
            return work_log, True  # True indicates created new
