from django import forms
from datetime import date
from .models import Income
from categories.models import Category


class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = [
            "description",
            "amount",
            "payer",
            "date",
            "category",
            "is_taxable",
            "attachment",
        ]
        widgets = {
            "description": forms.TextInput(
                attrs={"class": "form-control", "required": True}
            ),
            "amount": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "min": "0"}
            ),
            "payer": forms.TextInput(attrs={"class": "form-control", "required": True}),
            "date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "category": forms.Select(attrs={"class": "form-select", "required": True}),
            "is_taxable": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "attachment": forms.FileInput(
                attrs={
                    "class": "form-control",
                    "accept": ".pdf,.jpg,.jpeg,.png,.gif,.doc,.docx,.xls,.xlsx",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["date"].initial = date.today()
        # All categories are now available for income
        self.fields["category"].queryset = Category.objects.all()

    def clean(self):
        cleaned_data = super().clean()

        return cleaned_data
