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
        is_taxable = cleaned_data.get("is_taxable")
        attachment = cleaned_data.get("attachment")

        # If income is taxable, attachment is recommended but not required
        # We'll keep it optional for now, but could make it required if needed
        if is_taxable and not attachment:
            # Just add a warning, don't fail validation
            self.add_error(
                "attachment", "Consider uploading documentation for taxable income."
            )

        return cleaned_data
