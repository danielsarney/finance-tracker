from django.shortcuts import redirect
from django.urls import reverse


class TwoFactorAuthMiddleware:
    """
    Middleware to enforce 2FA verification for authenticated users.
    Users must verify their 2FA token before accessing protected pages.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # URLs that don't require 2FA verification
        exempt_urls = [
            "/accounts/login/",
            "/accounts/register/",
            "/accounts/logout/",
            "/twofa/setup/",
            "/twofa/verify/",
            "/twofa/status/",
            "/twofa/verify-ajax/",
            "/twofa/logout/",
            "/static/",
            "/admin/",
        ]

        # Check if current URL is exempt
        current_path = request.path
        is_exempt = any(current_path.startswith(url) for url in exempt_urls)

        # Only check 2FA for authenticated users on non-exempt URLs
        if (
            request.user.is_authenticated
            and not is_exempt
            and not request.path.startswith("/admin/")
        ):

            # Check if user has 2FA enabled
            if hasattr(request.user, "twofa") and request.user.twofa.is_enabled:
                # Check if 2FA is verified in this session
                if not request.session.get("twofa_verified", False):
                    # Redirect to 2FA verification (no message needed)
                    return redirect(f"{reverse('twofa:verify')}?next={current_path}")
            else:
                # User doesn't have 2FA enabled, redirect to setup (no message needed)
                return redirect("twofa:setup")

        response = self.get_response(request)
        return response
