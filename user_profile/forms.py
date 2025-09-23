from django import forms
from .models import UserProfile


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            "address_line_1",
            "address_line_2",
            "town",
            "post_code",
            "email",
            "phone",
            "bank_name",
            "account_number",
            "account_name",
            "sort_code",
        ]
        widgets = {
            "address_line_1": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g., 123 Business Street",
                }
            ),
            "address_line_2": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "e.g., Suite 456"}
            ),
            "town": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "e.g., London"}
            ),
            "post_code": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "e.g., SW1A 1AA"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "your@email.com"}
            ),
            "phone": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "+44 123 456 7890"}
            ),
            "bank_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "e.g., Barclays Bank"}
            ),
            "account_number": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "12345678"}
            ),
            "account_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Your Business Name"}
            ),
            "sort_code": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "12-34-56"}
            ),
        }
        labels = {
            "address_line_1": "Address Line 1",
            "address_line_2": "Address Line 2",
            "town": "Town/City",
            "post_code": "Post Code",
            "email": "Business Email",
            "phone": "Business Phone",
            "bank_name": "Bank Name",
            "account_number": "Account Number",
            "account_name": "Account Name",
            "sort_code": "Sort Code",
        }
