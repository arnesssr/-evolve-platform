from django.apps import AppConfig


class BusinessConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'App.business'
    verbose_name = 'Business Customer Dashboard'
    
    def ready(self):
        # Import signal handlers when app is ready
        try:
            import App.business.signals  # noqa F401
        except ImportError:
            pass
