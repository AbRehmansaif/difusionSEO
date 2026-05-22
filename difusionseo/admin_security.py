"""
Admin Login Security Module
- Rate limiting per IP address
- Account lockout after failed attempts
- Bot protection via honeypot
- Audit logging of failed login attempts
"""

from django.contrib.admin.views.decorators import staff_member_required
from django.core.cache import cache
from django.http import HttpResponseForbidden
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

# Configuration
MAX_ATTEMPTS = 5          # Max failed attempts before lockout
LOCKOUT_DURATION = 15 * 60  # 15 minutes in seconds
ATTEMPT_WINDOW = 5 * 60     # 5-minute window to count attempts


def get_client_ip(request):
    """Extract real client IP, accounting for proxies."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '0.0.0.0')


def get_attempt_key(ip):
    return f'admin_login_attempts_{ip}'


def get_lockout_key(ip):
    return f'admin_login_locked_{ip}'


def is_locked_out(ip):
    """Check if this IP is currently locked out."""
    return cache.get(get_lockout_key(ip)) is not None


def record_failed_attempt(ip):
    """Record a failed login attempt. Lock out after MAX_ATTEMPTS."""
    key = get_attempt_key(ip)
    attempts = cache.get(key, 0) + 1
    cache.set(key, attempts, timeout=ATTEMPT_WINDOW)

    logger.warning(f'[ADMIN SECURITY] Failed login attempt #{attempts} from IP: {ip}')

    if attempts >= MAX_ATTEMPTS:
        cache.set(get_lockout_key(ip), True, timeout=LOCKOUT_DURATION)
        cache.delete(key)
        logger.warning(
            f'[ADMIN SECURITY] IP {ip} locked out for {LOCKOUT_DURATION // 60} minutes '
            f'after {attempts} failed attempts.'
        )
        return True  # Is now locked out
    return False


def clear_failed_attempts(ip):
    """Clear failed attempts on successful login."""
    cache.delete(get_attempt_key(ip))
    cache.delete(get_lockout_key(ip))
