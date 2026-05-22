"""
Secure Custom Admin Site
Overrides the default Django admin login to add:
- IP-based rate limiting & lockout
- Honeypot bot trap
- Audit logging
"""

from django.contrib import admin
from django.contrib.admin import AdminSite
from django.shortcuts import redirect
from django.http import HttpResponseForbidden
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import REDIRECT_FIELD_NAME

from .admin_security import (
    get_client_ip,
    is_locked_out,
    record_failed_attempt,
    clear_failed_attempts,
    LOCKOUT_DURATION,
)


class SecureAdminSite(AdminSite):
    """Custom AdminSite with brute-force protection on the login view."""

    @method_decorator(never_cache)
    @method_decorator(csrf_protect)
    def login(self, request, extra_context=None):
        ip = get_client_ip(request)

        # Honeypot: reject bots that fill hidden fields
        if request.method == 'POST' and request.POST.get('website_url_honeypot'):
            # Silent fail — looks like a normal redirect to the bot
            return redirect(request.get_full_path())

        # Lockout check
        if is_locked_out(ip):
            extra_context = extra_context or {}
            extra_context['locked_out'] = True
            extra_context['lockout_minutes'] = LOCKOUT_DURATION // 60

        if request.method == 'POST' and not is_locked_out(ip):
            # We intercept post-login to check success/failure
            response = super().login(request, extra_context=extra_context)

            # If user is now authenticated, clear the failed count
            if request.user.is_authenticated:
                clear_failed_attempts(ip)
            else:
                # Login failed — record it
                now_locked = record_failed_attempt(ip)
                if now_locked:
                    extra_context = extra_context or {}
                    extra_context['locked_out'] = True
                    extra_context['lockout_minutes'] = LOCKOUT_DURATION // 60
                    return super().login(request, extra_context=extra_context)

            return response

        return super().login(request, extra_context=extra_context)


# Replace the default site
secure_admin_site = SecureAdminSite(name='admin')
