from django.apps import AppConfig


class AdminConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'App.admin'
    label = 'platform_admin'
    verbose_name = 'Platform Administration'
    
    def ready(self):
        # Import signal handlers when app is ready
        try:
            import App.admin.signals  # noqa F401
        except ImportError:
            pass
