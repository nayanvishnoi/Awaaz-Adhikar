import time
from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import redirect

class AbsoluteSessionLimitMiddleware:
    """Expire a login 45 minutes after sign-in even if session is modified."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            started_at = request.session.get('login_started_at')
            if started_at is None:
                # Existing logged-in Step 4 sessions receive the new limit.
                request.session['login_started_at'] = int(time.time())
                request.session.set_expiry(45 * 60)
            elif time.time() - started_at >= 45 * 60:
                logout(request)
                messages.warning(request, 'Your 45-minute session expired. Please log in again.')
                return redirect('login')
        return self.get_response(request)
