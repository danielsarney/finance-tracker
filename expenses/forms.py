from django import forms
from datetime import date
from .models import Expense
from categories.models import Category

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['amount', 'description', 'payee', 'date', 'category', 'is_taxable', 'notes']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'payee': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'category': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'is_taxable': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].initial = date.today()
        # Filter categories to only show expense types
        self.fields['category'].queryset = Category.objects.filter(category_type='expense')
