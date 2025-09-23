from django import forms
from datetime import date
from .models import WorkLog
from clients.models import Client


class WorkLogForm(forms.ModelForm):
    class Meta:
        model = WorkLog
        fields = [
            "company_client",
            "hours_worked",
            "hourly_rate",
            "work_date",
            "status",
            "invoice_date",
            "payment_date",
            "invoice_number",
        ]
        widgets = {
            "company_client": forms.Select(
                attrs={"class": "form-control", "id": "id_company_client"}
            ),
            "hours_worked": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.25", "min": "0"}
            ),
            "hourly_rate": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                    "id": "id_hourly_rate",
                }
            ),
            "work_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "status": forms.Select(attrs={"class": "form-control"}),
            "invoice_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "payment_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "invoice_number": forms.TextInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["work_date"].initial = date.today()

        # Filter clients to only show the current user's clients
        if "instance" in kwargs and kwargs["instance"]:
            user = kwargs["instance"].user
        else:
            # For new work logs, we'll need to get the user from the request
            # This will be handled in the view
            user = None

        if user:
            self.fields["company_client"].queryset = Client.objects.filter(
                user=user
            ).order_by("company_name")

    def set_user(self, user):
        """Set the user to filter clients for this user only."""
        self.fields["company_client"].queryset = Client.objects.filter(
            user=user
        ).order_by("company_name")
