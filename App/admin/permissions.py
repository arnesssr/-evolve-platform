# Admin permissions placeholder. Implement real checks (e.g., is_staff or group/perm).
from django.contrib.auth.mixins import UserPassesTestMixin
from django.conf import settings

class AdminRequiredMixin(UserPassesTestMixin):
    # Do not raise PermissionDenied; redirect to login when possible
    raise_exception = False

    def test_func(self):
        user = self.request.user
        # In development, allow any authenticated user to pass to avoid 403 during setup
        if getattr(settings, 'DEBUG', False):
            return user.is_authenticated
        # In production, require staff or superuser
        return user.is_authenticated and (getattr(user, 'is_staff', False) or getattr(user, 'is_superuser', False))

