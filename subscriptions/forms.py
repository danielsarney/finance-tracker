from django import forms
from datetime import date
from .models import Subscription
from categories.models import Category

class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = ['name', 'amount', 'date', 'billing_cycle', 'start_date', 'next_billing_date', 'category']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'billing_cycle': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'next_billing_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'category': forms.Select(attrs={'class': 'form-select', 'required': True}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].initial = date.today()
        self.fields['start_date'].initial = date.today()
        self.fields['next_billing_date'].initial = date.today()
        # All categories are now available for subscriptions
        self.fields['category'].queryset = Category.objects.all()
