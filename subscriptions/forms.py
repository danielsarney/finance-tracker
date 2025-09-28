from django import forms
from datetime import date
from .models import Subscription
from categories.models import Category


class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = [
            "name",
            "amount",
            "date",
            "billing_cycle",
            "next_billing_date",
            "category",
            "is_auto_renewed",
            "is_business_expense",
            "attachment",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "amount": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "min": "0"}
            ),
            "date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "billing_cycle": forms.Select(attrs={"class": "form-select"}),
            "next_billing_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "category": forms.Select(attrs={"class": "form-select", "required": True}),
            "is_auto_renewed": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "is_business_expense": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
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
        self.fields["next_billing_date"].initial = date.today()
        self.fields["category"].queryset = Category.objects.all()

    def clean(self):
        cleaned_data = super().clean()
        is_business_expense = cleaned_data.get("is_business_expense")
        attachment = cleaned_data.get("attachment")

        # If subscription is a business expense, attachment is recommended but not required
        # We'll keep it optional for now, but could make it required if needed
        if is_business_expense and not attachment:
            # Just add a warning, don't fail validation
            self.add_error(
                "attachment", "Consider uploading documentation for business expenses."
            )

        return cleaned_data
