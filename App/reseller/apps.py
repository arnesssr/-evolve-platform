"""Reseller app configuration."""
from django.apps import AppConfig


class ResellerConfig(AppConfig):
    """Configuration for the reseller application."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'App.reseller'
    verbose_name = 'Reseller Management'
