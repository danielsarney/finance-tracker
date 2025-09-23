from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomAuthenticationForm


def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            # Redirect to 2FA setup since it's mandatory
            return redirect("twofa:setup")
        else:
            # Handle form errors as flash messages
            if form.non_field_errors():
                for error in form.non_field_errors():
                    messages.error(request, error, extra_tags="danger")
            else:
                messages.error(
                    request, "Please correct the errors below.", extra_tags="danger"
                )
    else:
        form = CustomUserCreationForm()

    return render(request, "accounts/register.html", {"form": form})


def user_login(request):
    if request.method == "POST":
        form = CustomAuthenticationForm(request.POST)
        if form.is_valid():
            user = form.user
            login(request, user)

            # Check if user has 2FA enabled
            if hasattr(user, "twofa") and user.twofa.is_enabled:
                # Redirect to 2FA verification
                return redirect("twofa:verify")
            else:
                # Redirect to 2FA setup
                return redirect("twofa:setup")
        else:
            # Handle authentication errors as flash messages
            if form.non_field_errors():
                for error in form.non_field_errors():
                    messages.error(request, error, extra_tags="danger")
            else:
                messages.error(
                    request, "Please correct the errors below.", extra_tags="danger"
                )
    else:
        form = CustomAuthenticationForm()

    return render(request, "accounts/login.html", {"form": form})


@login_required
def user_logout(request):
    logout(request)
    return redirect("accounts:login")
