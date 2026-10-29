import time
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect

SESSION_SECONDS = 45 * 60

class ParticipantLoginView(LoginView):
    template_name = 'login.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        self.request.session['login_started_at'] = int(time.time())
        self.request.session.set_expiry(SESSION_SECONDS)
        messages.success(self.request, 'Login successful! Welcome back.')
        return response

class ParticipantLogoutView(LogoutView):
    def post(self, request, *args, **kwargs):
        logout(request)
        messages.success(request, 'Logout successful! See you again.')
        return redirect('home')
