"""
Admin Login Security Middleware
Intercepts all POST requests to /admin/login/ and applies:
- IP-based rate limiting (5 attempts per 5 minutes)
- 15-minute lockout after exceeding limit
- Honeypot bot trap
"""

from django.shortcuts import redirect
from django.http import HttpResponseForbidden
from .admin_security import (
    get_client_ip,
    is_locked_out,
    record_failed_attempt,
    clear_failed_attempts,
    LOCKOUT_DURATION,
)


class AdminLoginSecurityMiddleware:
    """Middleware to protect the Django admin login from brute force and bots."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin/login/') and request.method == 'POST':
            ip = get_client_ip(request)

            # 1. Honeypot — bots fill all inputs blindly
            if request.POST.get('website_url_honeypot'):
                # Looks like success to bot, but nothing happens
                return redirect('/admin/login/')

            # 2. Check if already locked out before even processing
            if is_locked_out(ip):
                return HttpResponseForbidden(
                    f'<html><body style="font-family:sans-serif;background:#0a0a0f;color:white;display:flex;'
                    f'align-items:center;justify-content:center;min-height:100vh;margin:0;">'
                    f'<div style="text-align:center;padding:40px;border:1px solid rgba(239,68,68,0.3);'
                    f'border-radius:16px;background:rgba(239,68,68,0.08);max-width:400px;">'
                    f'<h2 style="color:#fca5a5;margin-bottom:12px;">🔒 Access Temporarily Blocked</h2>'
                    f'<p style="color:rgba(255,255,255,0.6);font-size:0.9rem;">'
                    f'Too many failed login attempts. Try again in <strong style="color:white;">'
                    f'{LOCKOUT_DURATION // 60} minutes</strong>.</p>'
                    f'</div></body></html>'
                )

            # 3. Let Django process the login normally
            response = self.get_response(request)

            # 4. Check login result: if still on login page → login failed
            if response.status_code in (200, 302):
                # A redirect to /admin/ means SUCCESS
                location = response.get('Location', '')
                if response.status_code == 302 and '/admin/' in location and 'login' not in location:
                    clear_failed_attempts(ip)
                elif response.status_code == 200:
                    # Still on login page = failed attempt
                    record_failed_attempt(ip)

            return response

        return self.get_response(request)
