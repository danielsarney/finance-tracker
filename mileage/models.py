from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
from datetime import date


class MileageLog(models.Model):
    """
    Model to track business mileage for tax deduction purposes.
    Implements UK mileage rates: 45p/mile for first 10,000 miles, 25p/mile thereafter.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mileage_logs')
    date = models.DateField(help_text="Date of the journey")
    
    # Journey details
    start_location = models.CharField(max_length=200, help_text="Starting location (e.g., Home Office)")
    end_location = models.CharField(max_length=200, help_text="Destination (e.g., Client Office)")
    purpose = models.CharField(max_length=200, help_text="Business purpose of the journey")
    
    # Address details for HMRC compliance
    start_address = models.TextField(help_text="Full address of starting location")
    end_address = models.TextField(help_text="Full address of destination")
    
    # Mileage details
    miles = models.DecimalField(max_digits=6, decimal_places=1, help_text="Number of miles driven")
    
    # Client association
    client = models.ForeignKey('clients.Client', on_delete=models.PROTECT, 
                              help_text="Client for this business journey")
    
    # Calculated fields
    rate_per_mile = models.DecimalField(max_digits=4, decimal_places=2, editable=False, 
                                       help_text="Rate per mile used for calculation")
    total_claim = models.DecimalField(max_digits=8, decimal_places=2, editable=False, 
                                     help_text="Total claimable amount")

    class Meta:
        ordering = ['-date']
        verbose_name = 'Mileage Log'
        verbose_name_plural = 'Mileage Logs'
    
    def __str__(self):
        return f"{self.start_location} to {self.end_location} - {self.miles} miles ({self.date})"
    
    def save(self, *args, **kwargs):
        """Calculate rate and total claim based on UK mileage rules."""
        if not self.pk:  # Only calculate on creation
            self.calculate_claim()
        super().save(*args, **kwargs)
    
    def calculate_claim(self):
        """Calculate the claimable amount based on UK mileage rates."""
        # Convert miles to Decimal for consistent calculations
        miles_decimal = Decimal(str(self.miles))
        
        # Get total miles for this user in the current tax year
        current_year = self.date.year
        tax_year_start = date(current_year, 4, 6)  # UK tax year starts April 6th
        
        # If the journey is before April 6th, it belongs to the previous tax year
        if self.date < tax_year_start:
            tax_year_start = date(current_year - 1, 4, 6)
        
        tax_year_end = date(tax_year_start.year + 1, 4, 5)
        
        # Get total miles for this user in the current tax year (excluding this record)
        existing_miles = MileageLog.objects.filter(
            user=self.user,
            date__gte=tax_year_start,
            date__lte=tax_year_end
        ).exclude(pk=self.pk).aggregate(
            total=models.Sum('miles')
        )['total'] or Decimal('0')
        
        # Calculate which rate to use
        total_miles_in_year = existing_miles + miles_decimal
        
        if total_miles_in_year <= 10000:
            # All miles at 45p rate
            self.rate_per_mile = Decimal('0.45')
            self.total_claim = miles_decimal * Decimal('0.45')
        elif existing_miles < 10000:
            # Some miles at 45p, some at 25p
            miles_at_45p = Decimal('10000') - existing_miles
            miles_at_25p = miles_decimal - miles_at_45p
            
            self.rate_per_mile = Decimal('0.45')  # Primary rate for this journey
            self.total_claim = (miles_at_45p * Decimal('0.45')) + (miles_at_25p * Decimal('0.25'))
        else:
            # All miles at 25p rate
            self.rate_per_mile = Decimal('0.25')
            self.total_claim = miles_decimal * Decimal('0.25')
    
    @property
    def effective_rate_per_mile(self):
        """Get the effective rate per mile for this journey."""
        if self.miles > 0:
            return self.total_claim / Decimal(str(self.miles))
        return Decimal('0')
    
    @classmethod
    def get_tax_year_summary(cls, user, year):
        """Get mileage summary for a specific tax year."""
        # UK tax year runs from April 6th to April 5th
        if year >= 4:  # April onwards
            tax_year_start = date(year, 4, 6)
            tax_year_end = date(year + 1, 4, 5)
        else:  # Before April
            tax_year_start = date(year - 1, 4, 6)
            tax_year_end = date(year, 4, 5)
        
        logs = cls.objects.filter(
            user=user,
            date__gte=tax_year_start,
            date__lte=tax_year_end
        )
        
        total_miles = sum(log.miles for log in logs)
        total_claim = sum(log.total_claim for log in logs)
        
        return {
            'total_miles': total_miles,
            'total_claim': total_claim,
            'miles_at_45p': min(total_miles, Decimal('10000')),
            'miles_at_25p': max(Decimal('0'), total_miles - Decimal('10000')),
            'logs_count': logs.count(),
            'tax_year_start': tax_year_start,
            'tax_year_end': tax_year_end,
        }