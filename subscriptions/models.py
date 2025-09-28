from django.db import models
from cloudinary.models import CloudinaryField
from cloudinary import uploader
from finance_tracker.mixins import BaseFinancialModel
import logging

logger = logging.getLogger(__name__)


class Subscription(BaseFinancialModel):
    BILLING_CYCLE_CHOICES = [
        ("DAILY", "Daily"),
        ("WEEKLY", "Weekly"),
        ("MONTHLY", "Monthly"),
        ("QUARTERLY", "Quarterly"),
        ("YEARLY", "Yearly"),
    ]

    name = models.CharField(max_length=200)
    billing_cycle = models.CharField(
        max_length=20, choices=BILLING_CYCLE_CHOICES, default="MONTHLY"
    )
    next_billing_date = models.DateField()
    is_auto_renewed = models.BooleanField(
        default=False, help_text="Whether this subscription automatically renews"
    )
    is_business_expense = models.BooleanField(
        default=False, help_text="Whether this subscription is a business expense"
    )
    attachment = CloudinaryField(
        "attachment",
        folder="finance_tracker/subscriptions",
        null=True,
        blank=True,
        help_text="Upload invoices, receipts, or bank statements",
    )

    class Meta:
        verbose_name = "Subscription"
        verbose_name_plural = "Subscriptions"
        ordering = ["next_billing_date", "name"]

    def save(self, *args, **kwargs):
        """Override save to handle attachment replacement and billing date logic."""
        # Handle attachment replacement
        if self.pk:
            try:
                # Get the old instance from database
                old_instance = Subscription.objects.get(pk=self.pk)
                old_attachment = old_instance.attachment

                # If there was an old attachment and it's different from the new one
                if old_attachment and old_attachment != self.attachment:
                    try:
                        # Delete the old file from Cloudinary
                        uploader.destroy(old_attachment.public_id)
                        logger.info(
                            f"Successfully replaced old Cloudinary file: {old_attachment.public_id}"
                        )
                    except Exception as e:
                        logger.error(
                            f"Error deleting old Cloudinary file {old_attachment.public_id}: {e}"
                        )
            except Subscription.DoesNotExist:
                # This is a new instance, no old attachment to clean up
                pass

        # Handle billing date logic
        if not self.next_billing_date:
            self.next_billing_date = self.date

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Override delete to also remove the Cloudinary file."""
        if self.attachment:
            try:
                # Delete the file from Cloudinary
                uploader.destroy(self.attachment.public_id)
                logger.info(
                    f"Successfully deleted Cloudinary file: {self.attachment.public_id}"
                )
            except Exception as e:
                # Log the error but don't prevent deletion
                logger.error(
                    f"Error deleting Cloudinary file {self.attachment.public_id}: {e}"
                )

        # Call the parent delete method
        super().delete(*args, **kwargs)
