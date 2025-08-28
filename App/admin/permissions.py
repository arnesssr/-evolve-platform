# Admin permissions placeholder. Implement real checks (e.g., is_staff or group/perm).
from django.contrib.auth.mixins import UserPassesTestMixin
from django.conf import settings
from django.contrib.auth.decorators import user_passes_test

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


def admin_required(function=None, redirect_field_name='next', login_url=None):
    """
    Function-based view decorator mirroring AdminRequiredMixin behavior.
    Redirects to settings.LOGIN_URL when user is not permitted.
    """
    def _test(user):
        if getattr(settings, 'DEBUG', False):
            return user.is_authenticated
        return user.is_authenticated and (getattr(user, 'is_staff', False) or getattr(user, 'is_superuser', False))

    actual_login_url = login_url or getattr(settings, 'LOGIN_URL', '/login/')
    decorator = user_passes_test(_test, login_url=actual_login_url, redirect_field_name=redirect_field_name)
    if function:
        return decorator(function)
    return decorator

