from django import forms
from .models import Client

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = [
            'company_name', 'contact_person', 'email', 'phone',
            'address_line_1', 'address_line_2', 'town', 'post_code',
            'hourly_rate'
        ]
        widgets = {
            'company_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Tech Startup Ltd'
            }),
            'contact_person': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., John Smith'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'john@techstartup.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+44 123 456 7890'
            }),
            'address_line_1': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 456 Business Park'
            }),
            'address_line_2': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Unit 7'
            }),
            'town': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Manchester'
            }),
            'post_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., M1 1AA'
            }),
            'hourly_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '45.00'
            }),
        }
        labels = {
            'company_name': 'Company Name',
            'contact_person': 'Contact Person',
            'email': 'Email',
            'phone': 'Phone',
            'address_line_1': 'Address Line 1',
            'address_line_2': 'Address Line 2',
            'town': 'Town/City',
            'post_code': 'Post Code',
            'hourly_rate': 'Hourly Rate (£)',
        }
