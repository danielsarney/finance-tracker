from django import forms
from datetime import date
from .models import WorkLog, ClockSession
from clients.models import Client


class WorkLogForm(forms.ModelForm):
    # Custom field for intuitive time entry
    hours_worked_intuitive = forms.CharField(
        label="Hours Worked",
        help_text="Enter time in format like 1.10 for 1 hour 10 minutes, or 0.30 for 30 minutes",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "e.g., 1.10 for 1h 10m, 0.30 for 30m",
            }
        ),
        required=False,  # Make it optional since we also have hours_worked
    )

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
                attrs={
                    "class": "form-control",
                    "step": "0.25",
                    "min": "0",
                    "id": "id_hours_worked",
                }
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
            # Convert existing hours_worked to intuitive format for editing
            if kwargs["instance"].hours_worked:
                intuitive_time = WorkLog.convert_decimal_to_intuitive(
                    float(kwargs["instance"].hours_worked)
                )
                self.fields["hours_worked_intuitive"].initial = intuitive_time
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

    def clean_hours_worked_intuitive(self):
        """Convert intuitive time format to decimal hours"""
        intuitive_time = self.cleaned_data.get("hours_worked_intuitive")
        if intuitive_time:
            try:
                decimal_hours = WorkLog.convert_intuitive_to_decimal(intuitive_time)
                # Set the actual hours_worked field
                self.cleaned_data["hours_worked"] = decimal_hours
                return intuitive_time
            except ValueError as e:
                raise forms.ValidationError(str(e))
        return intuitive_time

    def clean(self):
        """Clean form data and handle hours_worked conversion"""
        cleaned_data = super().clean()

        # If hours_worked_intuitive is provided, use it to set hours_worked
        intuitive_time = cleaned_data.get("hours_worked_intuitive")
        if intuitive_time:
            try:
                decimal_hours = WorkLog.convert_intuitive_to_decimal(intuitive_time)
                cleaned_data["hours_worked"] = decimal_hours
            except ValueError as e:
                raise forms.ValidationError({"hours_worked_intuitive": str(e)})

        return cleaned_data


class ClockInForm(forms.ModelForm):
    """Form for clocking in"""

    class Meta:
        model = ClockSession
        fields = ["client"]
        widgets = {
            "client": forms.Select(attrs={"class": "form-control", "id": "id_client"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if user:
            self.fields["client"].queryset = Client.objects.filter(user=user).order_by(
                "company_name"
            )
