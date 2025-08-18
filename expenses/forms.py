from django import forms
from datetime import date
from .models import Expense
from categories.models import Category

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['description', 'amount', 'payee', 'date', 'category']
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'payee': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'category': forms.Select(attrs={'class': 'form-select', 'required': True}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].initial = date.today()
        # All categories are now available for expenses
        self.fields['category'].queryset = Category.objects.all()
