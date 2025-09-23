from django import forms
from .models import TwoFactorAuth


class TwoFactorSetupForm(forms.Form):
    """Form for setting up 2FA"""

    token = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter 6-digit code",
                "maxlength": "6",
                "pattern": "[0-9]{6}",
                "autocomplete": "off",
            }
        ),
        help_text="Enter the 6-digit code from your authenticator app",
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    def clean_token(self):
        token = self.cleaned_data.get("token")
        if not token or not token.isdigit() or len(token) != 6:
            raise forms.ValidationError("Please enter a valid 6-digit code.")

        if self.user:
            try:
                twofa = self.user.twofa
                if not twofa.verify_token(token):
                    raise forms.ValidationError(
                        "Invalid verification code. Please try again."
                    )
            except TwoFactorAuth.DoesNotExist:
                raise forms.ValidationError("2FA setup not found. Please try again.")
        else:
            raise forms.ValidationError("User context required for token validation.")

        return token


class TwoFactorVerifyForm(forms.Form):
    """Form for verifying 2FA token"""

    token = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter 6-digit code",
                "maxlength": "6",
                "pattern": "[0-9]{6}",
                "autocomplete": "off",
                "autofocus": True,
            }
        ),
        help_text="Enter the 6-digit code from your authenticator app",
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    def clean_token(self):
        token = self.cleaned_data.get("token")

        if not token:
            raise forms.ValidationError("Please enter a verification code.")

        if not token.isdigit() or len(token) != 6:
            raise forms.ValidationError("Please enter a valid 6-digit code.")

        if self.user:
            try:
                twofa = self.user.twofa
                if not twofa.verify_token(token):
                    raise forms.ValidationError(
                        "Invalid verification code. Please try again."
                    )
            except TwoFactorAuth.DoesNotExist:
                raise forms.ValidationError("2FA not configured for this account.")
        else:
            raise forms.ValidationError("User context required for token validation.")

        return token
