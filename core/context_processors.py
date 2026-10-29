import time

def session_timer(request):
    remaining = None
    if request.user.is_authenticated:
        started = request.session.get('login_started_at')
        if started is not None:
            remaining = max(0, 45 * 60 - int(time.time() - started))
    return {'session_remaining_seconds': remaining}
