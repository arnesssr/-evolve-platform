# Admin permissions placeholder. Implement real checks (e.g., is_staff or group/perm).
from django.contrib.auth.mixins import UserPassesTestMixin

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        return user.is_authenticated and (getattr(user, 'is_staff', False) or getattr(user, 'is_superuser', False))

