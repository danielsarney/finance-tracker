from django.db import models
from django.contrib.auth.models import User

class Client(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='clients')
    company_name = models.CharField(max_length=200, help_text="Company or client name")
    contact_person = models.CharField(max_length=100, help_text="Primary contact person")
    email = models.EmailField(help_text="Primary contact email")
    phone = models.CharField(max_length=20, blank=True, help_text="Contact phone number")
    address_line_1 = models.CharField(max_length=200, help_text="Company address line 1")
    address_line_2 = models.CharField(max_length=200, blank=True, help_text="Company address line 2 (optional)")
    town = models.CharField(max_length=100, help_text="Town or city")
    post_code = models.CharField(max_length=20, help_text="Postal code")
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, help_text="Default hourly rate for this client")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.company_name
    
    class Meta:
        ordering = ['company_name']
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'
    
    @property
    def full_address(self):
        """Return the complete formatted address"""
        address_parts = [self.address_line_1]
        if self.address_line_2:
            address_parts.append(self.address_line_2)
        address_parts.extend([self.town, self.post_code])
        return ', '.join(address_parts)
