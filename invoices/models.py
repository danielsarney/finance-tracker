from django.db import models
from django.contrib.auth.models import User
from clients.models import Client
from work.models import WorkLog


class Invoice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="invoices")
    invoice_number = models.CharField(
        max_length=20, unique=True, help_text="Auto-generated invoice number"
    )
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name="invoices"
    )
    issue_date = models.DateField()
    due_date = models.DateField()

    # Store sender details at creation time (locked)
    sender_name = models.CharField(
        max_length=200, blank=True, help_text="Sender name at time of invoice creation"
    )
    sender_address_line_1 = models.CharField(
        max_length=200,
        blank=True,
        help_text="Sender address line 1 at time of invoice creation",
    )
    sender_address_line_2 = models.CharField(
        max_length=200,
        blank=True,
        help_text="Sender address line 2 at time of invoice creation",
    )
    sender_town = models.CharField(
        max_length=100, blank=True, help_text="Sender town at time of invoice creation"
    )
    sender_post_code = models.CharField(
        max_length=20,
        blank=True,
        help_text="Sender post code at time of invoice creation",
    )
    sender_phone = models.CharField(
        max_length=20, blank=True, help_text="Sender phone at time of invoice creation"
    )
    sender_email = models.EmailField(
        blank=True, help_text="Sender email at time of invoice creation"
    )

    # Store bank details at creation time (locked)
    bank_name = models.CharField(
        max_length=100, blank=True, help_text="Bank name at time of invoice creation"
    )
    account_name = models.CharField(
        max_length=100, blank=True, help_text="Account name at time of invoice creation"
    )
    account_number = models.CharField(
        max_length=20,
        blank=True,
        help_text="Account number at time of invoice creation",
    )
    sort_code = models.CharField(
        max_length=10, blank=True, help_text="Sort code at time of invoice creation"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-issue_date"]
        verbose_name = "Invoice"
        verbose_name_plural = "Invoices"

    def __str__(self):
        return f"{self.invoice_number} - {self.client.company_name}"

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = self.generate_invoice_number()
        super().save(*args, **kwargs)

    @classmethod
    def generate_invoice_number(cls):
        """Generate next invoice number starting from INV-005"""
        # Get all existing invoice numbers and extract the numeric part
        existing_numbers = []
        for invoice in cls.objects.all():
            try:
                if invoice.invoice_number and invoice.invoice_number.startswith("INV-"):
                    number_part = invoice.invoice_number.split("-")[1]
                    existing_numbers.append(int(number_part))
            except (IndexError, ValueError):
                continue

        if existing_numbers:
            next_number = max(existing_numbers) + 1
        else:
            next_number = 5

        return f"INV-{next_number:03d}"

    @property
    def total_amount(self):
        """Calculate total from linked work logs"""
        return sum(item.work_log.total_amount for item in self.line_items.all())

    @property
    def is_paid(self):
        """Check if all work logs are paid"""
        line_items = self.line_items.all()
        if not line_items.exists():
            return False  # No line items means not paid
        return all(item.work_log.status == "PAID" for item in line_items)

    @property
    def is_overdue(self):
        """Check if invoice is overdue"""
        from django.utils import timezone

        return self.due_date < timezone.now().date() and not self.is_paid


class InvoiceLineItem(models.Model):
    invoice = models.ForeignKey(
        Invoice, on_delete=models.CASCADE, related_name="line_items"
    )
    work_log = models.ForeignKey(
        WorkLog, on_delete=models.CASCADE, related_name="invoice_line_items"
    )

    def __str__(self):
        return f"{self.invoice.invoice_number} - {self.work_log}"
