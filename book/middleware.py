from django.contrib.auth import logout
from django.conf import settings
from datetime import datetime, timedelta


class AutoLogoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # check if user is authenticated
        if request.user.is_authenticated:
            # Get last activity time from session
            if 'last_activity' in request.session:
                last_activity_str = request.session.get('last_activity')
                last_activity = datetime.fromisoformat(last_activity_str)
            else:
                last_activity = datetime.now()
            # calculate idle time
            idle_time = datetime.now() - last_activity
            # check if idle time is greater than the specified duration
            if idle_time > timedelta(seconds=settings.AUTO_LOGOUT_SECONDS):
                logout(request)
            # update last activity time in session
            if request.session is not None:
                request.session['last_activity'] = datetime.now().isoformat()
            response = self.get_response(request)
            return response
        else:
            return self.get_response(request)
        