from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    address_line_1 = models.CharField(
        max_length=200, help_text="Your business address line 1"
    )
    address_line_2 = models.CharField(
        max_length=200, blank=True, help_text="Your business address line 2 (optional)"
    )
    town = models.CharField(max_length=100, help_text="Your town or city")
    post_code = models.CharField(max_length=20, help_text="Your post code")
    email = models.EmailField(help_text="Your business email")
    phone = models.CharField(max_length=20, help_text="Your business phone number")
    bank_name = models.CharField(max_length=100, help_text="Your bank name")
    account_number = models.CharField(
        max_length=20, help_text="Your bank account number"
    )
    account_name = models.CharField(max_length=100, help_text="Name on the account")
    sort_code = models.CharField(
        max_length=10, help_text="Your bank sort code (e.g., 12-34-56)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"


# Signal to automatically create a profile when a user is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
