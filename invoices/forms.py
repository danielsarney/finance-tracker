from django import forms
from .models import Invoice
from clients.models import Client
from datetime import date, timedelta


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ["client", "issue_date", "due_date"]
        widgets = {
            "client": forms.Select(
                attrs={
                    "class": "form-select form-select-lg",
                    "style": "font-size: 16px; padding: 12px; border-radius: 8px; border: 2px solid #e9ecef; transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;",
                    "onchange": 'this.style.borderColor = this.value ? "#28a745" : "#e9ecef";',
                }
            ),
            "issue_date": forms.DateInput(
                attrs={
                    "class": "form-control form-control-lg",
                    "type": "date",
                    "style": "font-size: 16px; padding: 12px; border-radius: 8px; border: 2px solid #e9ecef;",
                }
            ),
            "due_date": forms.DateInput(
                attrs={
                    "class": "form-control form-control-lg",
                    "type": "date",
                    "style": "font-size: 16px; padding: 12px; border-radius: 8px; border: 2px solid #e9ecef;",
                }
            ),
        }
        labels = {
            "client": "Select Client",
            "issue_date": "Issue Date",
            "due_date": "Due Date",
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields["client"].queryset = Client.objects.filter(user=user).order_by(
                "company_name"
            )

        # Set default dates
        self.fields["issue_date"].initial = date.today()
        self.fields["due_date"].initial = date.today() + timedelta(days=30)

    def clean(self):
        cleaned_data = super().clean()
        issue_date = cleaned_data.get("issue_date")
        due_date = cleaned_data.get("due_date")

        if issue_date and due_date:
            if issue_date > due_date:
                raise forms.ValidationError("Due date must be after issue date")

            if issue_date > date.today():
                raise forms.ValidationError("Issue date cannot be in the future")

        return cleaned_data
