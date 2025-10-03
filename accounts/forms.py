from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
import random


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "Enter your email"}
        ),
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Enter your first name"}
        ),
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Enter your last name"}
        ),
    )

    # Simple math CAPTCHA
    math_answer = forms.IntegerField(
        required=True,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Enter the answer"}
        ),
        label="",
    )

    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove username field
        if "username" in self.fields:
            del self.fields["username"]

        # Style password fields
        self.fields["password1"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Enter your password"}
        )
        self.fields["password2"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Confirm your password"}
        )

        # Generate random math question only if not POST data
        if not self.data:
            self.num1 = random.randint(1, 10)
            self.num2 = random.randint(1, 10)
            self.correct_answer = self.num1 + self.num2
        else:
            # If POST data, get the numbers from the form data
            self.num1 = int(self.data.get("num1", 0))
            self.num2 = int(self.data.get("num2", 0))
            self.correct_answer = self.num1 + self.num2

    def clean_math_answer(self):
        """Validate the math CAPTCHA answer"""
        user_answer = self.cleaned_data.get("math_answer")
        if user_answer != self.correct_answer:
            raise forms.ValidationError("Incorrect answer. Please try again.")
        return user_answer

    def save(self, commit=True):
        user = super().save(commit=False)
        # Set username to email for compatibility
        user.username = self.cleaned_data["email"]
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]

        if commit:
            user.save()

        return user

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already registered.")
        return email


class CustomAuthenticationForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "Enter your email"}
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Enter your password"}
        )
    )

    def clean(self):
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")

        if email and password:
            # Try to authenticate with email
            try:
                user = User.objects.get(email=email)
                user = authenticate(username=user.username, password=password)
                if user is None:
                    raise forms.ValidationError("Invalid email or password.")
                self.user = user
            except User.DoesNotExist:
                raise forms.ValidationError("Invalid email or password.")

        return self.cleaned_data
