from django.db import models
from cloudinary.models import CloudinaryField
from cloudinary import uploader
from finance_tracker.mixins import BaseFinancialModel
import logging

logger = logging.getLogger(__name__)


class Income(BaseFinancialModel):
    description = models.CharField(max_length=200)
    payer = models.CharField(max_length=100, blank=True, null=True)
    is_taxable = models.BooleanField(default=True)
    attachment = CloudinaryField(
        "attachment",
        folder="finance_tracker/income",
        null=True,
        blank=True,
        help_text="Upload invoices, receipts, or bank statements",
    )

    class Meta:
        verbose_name = "Income"
        verbose_name_plural = "Incomes"

    def save(self, *args, **kwargs):
        """Override save to handle attachment replacement."""
        # Check if this is an update (not a new creation)
        if self.pk:
            try:
                # Get the old instance from database
                old_instance = Income.objects.get(pk=self.pk)
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
            except Income.DoesNotExist:
                # This is a new instance, no old attachment to clean up
                pass

        # Call the parent save method
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
