"""
Rate limiting utilities for preventing bot attacks on authentication endpoints.
"""

import time
from functools import wraps
from django.core.cache import cache
from django.http import HttpResponse
from django.contrib import messages


def rate_limit(max_attempts=5, window_minutes=15, key_prefix="rate_limit"):
    """
    Rate limiting decorator that tracks attempts per IP address.

    Args:
        max_attempts: Maximum number of attempts allowed in the time window
        window_minutes: Time window in minutes for rate limiting
        key_prefix: Prefix for cache keys to avoid conflicts

    Returns:
        Decorated view function with rate limiting
    """

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Get client IP address
            ip_address = get_client_ip(request)

            # Create cache key
            cache_key = f"{key_prefix}_{ip_address}"

            # Get current attempts from cache
            attempts = cache.get(cache_key, [])
            current_time = time.time()

            # Remove old attempts outside the window
            window_seconds = window_minutes * 60
            attempts = [
                attempt_time
                for attempt_time in attempts
                if current_time - attempt_time < window_seconds
            ]

            # Check if rate limit exceeded
            if len(attempts) >= max_attempts:
                # Rate limit exceeded
                messages.error(
                    request,
                    f"Too many attempts. Please wait {window_minutes} minutes before trying again.",
                    extra_tags="danger",
                )

                # Return 429 response for all request methods
                return HttpResponse(
                    "Rate limit exceeded. Please try again later.", status=429
                )

            # Record this attempt
            attempts.append(current_time)
            cache.set(cache_key, attempts, window_seconds)

            # Call the original view
            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator


def get_client_ip(request):
    """
    Get the client's IP address from the request.
    Handles proxy headers for production environments.
    """
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0].strip()
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip
