from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth import logout
from .models import TwoFactorAuth
from .forms import TwoFactorSetupForm, TwoFactorVerifyForm
import json


@login_required
def setup_twofa(request):
    """Setup 2FA for the user"""
    try:
        twofa = request.user.twofa
    except TwoFactorAuth.DoesNotExist:
        twofa = TwoFactorAuth.objects.create(user=request.user)
        twofa.generate_secret()
        twofa.save()

    if request.method == "POST":
        form = TwoFactorSetupForm(request.POST, user=request.user)
        if form.is_valid():
            twofa.is_enabled = True
            backup_codes = twofa.generate_backup_codes()
            twofa.save()

            # Mark 2FA as verified in session
            request.session["twofa_verified"] = True

            return redirect("dashboard:dashboard")
    else:
        form = TwoFactorSetupForm(user=request.user)

    context = {
        "form": form,
        "qr_code": twofa.generate_qr_code(),
        "secret_key": twofa.secret_key,
        "manual_entry_key": twofa.secret_key,
    }
    return render(request, "twofa/setp_up.html", context)


@login_required
def verify_twofa(request):
    """Verify 2FA token"""
    if not hasattr(request.user, "twofa") or not request.user.twofa.is_enabled:
        messages.error(
            request, "Two-factor authentication is not enabled for your account."
        )
        return redirect("twofa:setup")

    if request.method == "POST":
        form = TwoFactorVerifyForm(request.POST, user=request.user)
        if form.is_valid():
            # Mark 2FA as verified in session
            request.session["twofa_verified"] = True

            # Redirect to intended page or dashboard
            next_url = request.GET.get("next", "dashboard:dashboard")
            return redirect(next_url)
        # If form is invalid, it will be re-rendered with errors
    else:
        form = TwoFactorVerifyForm(user=request.user)

    context = {"form": form, "next": request.GET.get("next", "dashboard:dashboard")}
    return render(request, "twofa/verify.html", context)


@login_required
def twofa_status(request):
    """Check 2FA status for the user"""
    try:
        twofa = request.user.twofa
        is_enabled = twofa.is_enabled
        backup_codes_count = len(twofa.backup_codes)
    except TwoFactorAuth.DoesNotExist:
        is_enabled = False
        backup_codes_count = 0

    return JsonResponse(
        {
            "is_enabled": is_enabled,
            "backup_codes_count": backup_codes_count,
            "is_verified": request.session.get("twofa_verified", False),
        }
    )


@require_http_methods(["POST"])
@csrf_exempt
def verify_twofa_ajax(request):
    """AJAX endpoint for 2FA verification"""
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "error": "Not authenticated"})

    try:
        data = json.loads(request.body)
        token = data.get("token")
        backup_code = data.get("backup_code")

        if not token and not backup_code:
            return JsonResponse({"success": False, "error": "No token provided"})

        try:
            twofa = request.user.twofa
        except TwoFactorAuth.DoesNotExist:
            return JsonResponse({"success": False, "error": "2FA not configured"})

        if token:
            if not token.isdigit() or len(token) != 6:
                return JsonResponse({"success": False, "error": "Invalid token format"})
            if not twofa.verify_token(token):
                return JsonResponse({"success": False, "error": "Invalid token"})

        if backup_code:
            if not twofa.verify_backup_code(backup_code.upper()):
                return JsonResponse({"success": False, "error": "Invalid backup code"})

        # Mark as verified in session
        request.session["twofa_verified"] = True
        return JsonResponse({"success": True})

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON"})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


def logout_view(request):
    """Custom logout that clears 2FA verification"""
    request.session.pop("twofa_verified", None)
    logout(request)
    return redirect("accounts:login")
