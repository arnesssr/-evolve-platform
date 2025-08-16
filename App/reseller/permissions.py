"""Permissions for reseller module."""
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.contrib import messages


class ResellerRequiredMixin(UserPassesTestMixin):
    """Mixin to ensure user has a reseller profile."""
    
    def test_func(self):
        """Check if user has reseller profile."""
        return hasattr(self.request.user, 'reseller_profile') and self.request.user.reseller_profile.is_active
    
    def handle_no_permission(self):
        """Handle case where user doesn't have permission."""
        messages.error(self.request, 'You need an active reseller account to access this page.')
        return redirect('home')


class ActiveResellerRequiredMixin(ResellerRequiredMixin):
    """Mixin to ensure user has an active and verified reseller profile."""
    
    def test_func(self):
        """Check if user has active and verified reseller profile."""
        if not super().test_func():
            return False
        return self.request.user.reseller_profile.is_verified
    
    def handle_no_permission(self):
        """Handle case where user doesn't have permission."""
        if hasattr(self.request.user, 'reseller_profile'):
            messages.warning(self.request, 'Your reseller account needs to be verified to access this feature.')
            return redirect('reseller:dashboard')
        return super().handle_no_permission()


def is_reseller(user):
    """Check if user is a reseller."""
    return hasattr(user, 'reseller_profile') and user.reseller_profile.is_active


def is_verified_reseller(user):
    """Check if user is a verified reseller."""
    return is_reseller(user) and user.reseller_profile.is_verified
